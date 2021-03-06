import numpy as np
import torch
import torch.nn.functional as F
from modules.trainer.regularization import mix_rbf_mmd2

from modules.trainer import UpdaterBase


class MMD(UpdaterBase):
    def __init__(self, params, network, pre_train=None):
        super().__init__(params, network, pre_train)

        self.one = self.FloatTensor([1])
        self.mone = self.one * -1

        # Set optimizer
        for name in self.models.keys():
            self.models.set_optim(net=name, optimizer=torch.optim.RMSprop, lr=self.params["optimizer"]["lr_" + name])

        # sigma for MMD
        base = 1.0
        sigma_list = [1, 2, 4, 8, 16]
        self.sigma_list = [sigma / base for sigma in sigma_list]

        # add fixed sample for testing
        self.fixed_samples = {
            "z_input": self.FloatTensor(
                np.random.normal(0, 1, (self.params["train"]["generated_size"], self.params["network"]["z_dim"])))
        }

    def update_parameters_discriminator(self, z, x, y):
        """
        Update Discriminator
        :param x:
        :param y:
        :return criterion:
        """

        # Check D with real data
        d_real = self.models["Dis"](x)

        # Check D with fake data generated by G
        gen_x = self.models["Gen"](z).detach()
        d_fake = self.models["Dis"](gen_x)

        # calculate criterion
        # compute biased MMD2 and use ReLU to prevent negative value
        loss = mix_rbf_mmd2(d_real, d_fake, self.sigma_list)
        loss = F.relu(loss)
        loss = torch.sqrt(loss)
        loss.backward(self.mone)
        return loss

    def update_parameters_generator(self, z, x, y):
        """
        Update Generator
        :param x:
        :param y:
        :return criterion:
        """

        # Check D with real data
        d_real = self.models["Dis"](x)

        # Check G net
        gen_x = self.models["Gen"](z)
        d_fake = self.models["Dis"](gen_x)

        # compute biased MMD2 and use ReLU to prevent negative value
        loss = mix_rbf_mmd2(d_real, d_fake, self.sigma_list)
        loss = F.relu(loss)
        # Calculate criterion
        loss = torch.sqrt(loss)
        loss.backward(self.one)
        return loss
