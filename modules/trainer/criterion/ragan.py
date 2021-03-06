import torch

from base import BaseGanCriterion


class Critic(BaseGanCriterion):
    def __init__(self, parent, regularization=None, **kwargs):
        super().__init__(parent=parent, regularization=regularization, **kwargs)

        if torch.cuda.is_available():
            self.fn_loss = torch.nn.BCEWithLogitsLoss().cuda()
        else:
            self.fn_loss = torch.nn.BCEWithLogitsLoss()

    def calculate(self, z, x, y):
        valid = self.Tensor.Float(x.shape[0], 1).fill_(1.0)
        fake = self.Tensor.Float(x.shape[0], 1).fill_(0.0)

        # Check D with real data
        critic_real = self.model["critic"](x)

        # Check D with fake data generated by G
        gen_x = self.model["generator"](z)
        critic_fake = self.model["critic"](gen_x)

        real_loss = self.fn_loss(critic_real - critic_fake.mean(0, keepdim=True), valid)
        fake_loss = self.fn_loss(critic_fake - critic_real.mean(0, keepdim=True), fake)

        loss = (real_loss + fake_loss) / 2

        # Return dict for regularization parameters
        reg_params = dict(
            network=self.model['critic'],
            real_data=x,
            fake_data=gen_x,
            critic_real=critic_real,
            critic_fake=critic_fake,
        )
        return loss, reg_params


class Generator(BaseGanCriterion):
    def __init__(self, parent, regularization=None, **kwargs):
        super().__init__(parent=parent, regularization=regularization, **kwargs)

        if torch.cuda.is_available():
            self.fn_loss = torch.nn.BCEWithLogitsLoss().cuda()
        else:
            self.fn_loss = torch.nn.BCEWithLogitsLoss()

    def calculate(self, z, x, y):
        fake = self.Tensor.Float(x.shape[0], 1).fill_(0.0)

        # Check D with real data
        critic_real = self.model["critic"](x)

        # Check D with fake data generated by G
        gen_x = self.model["generator"](z)
        critic_fake = self.model["critic"](gen_x)

        fake_loss = self.fn_loss(critic_fake - critic_real.mean(0, keepdim=True), fake)

        loss = fake_loss

        # Return dict for regularization parameters
        reg_params = dict(
            network=self.model['generator'],
            real_data=x,
            fake_data=gen_x,
            critic_real=critic_real,
            critic_fake=critic_fake,
        )
        return loss, reg_params
