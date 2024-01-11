import os
from termcolor import colored, cprint
import torch
import utils.util as util
import math

def create_model(opt):
    model = None

    if opt.model == 'sdfusion':
        from models.sdfusion_model import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_new':
        from models.sdfusion_model_new import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_LAS':
        from models.sdfusion_model_LAS import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_small':
        from models.sdfusion_model_small import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_large':
        from models.sdfusion_model_large import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_large_pred_x0':
        from models.sdfusion_model_large_pred_x0 import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_feature_lr_pred_x0':
        from models.sdfusion_model_feature_lr_pred_x0 import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_feature':
        from models.sdfusion_model_feature import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_feature_pred_x0':
        from models.sdfusion_model_feature_pred_x0 import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_union_two_time':
        from models.sdfusion_model_union_two_time import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_union_two_time_noise_octree':
        from models.sdfusion_model_union_two_time_noise_octree import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_union_three_time':
        from models.sdfusion_model_union_three_time import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_union_three_time_pred_x0':
        from models.sdfusion_model_union_three_time_pred_x0 import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_union_three_time_pred_noise':
        from models.sdfusion_model_union_three_time_pred_noise import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_union_three_time_noise_octree':
        from models.sdfusion_model_union_three_time_noise_octree import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion_union_four_time':
        from models.sdfusion_model_union_four_time import SDFusionModel
        model = SDFusionModel()

    elif opt.model == 'sdfusion-txt2shape':
        from models.sdfusion_txt2shape_model import SDFusionText2ShapeModel
        model = SDFusionText2ShapeModel()

    elif opt.model == 'sdfusion-img2shape':
        from models.sdfusion_img2shape_model import SDFusionImage2ShapeModel
        model = SDFusionImage2ShapeModel()

    elif opt.model == 'sdfusion-mm2shape':
        from models.sdfusion_mm_model import SDFusionMultiModal2ShapeModel
        model = SDFusionMultiModal2ShapeModel()

    else:
        raise ValueError("Model [%s] not recognized." % opt.model)

    model.initialize(opt)
    cprint("[*] Model has been created: %s" % model.name(), 'blue')
    return model


# modified from https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix
class BaseModel():
    def name(self):
        return 'BaseModel'

    def initialize(self, opt):
        self.opt = opt
        self.gpu_ids = opt.gpu_ids
        self.isTrain = opt.isTrain
        self.Tensor = torch.cuda.FloatTensor if self.gpu_ids else torch.Tensor

        self.model_names = []
        self.epoch_labels = []
        self.optimizers = []

    def set_input(self, input):
        self.input = input

    def forward(self):
        pass

    def get_image_paths(self):
        pass

    def optimize_parameters(self):
        pass

    def get_current_visuals(self):
        return self.input

    def get_current_errors(self):
        return {}

    # define the optimizers
    def set_optimizers(self):
        pass

    def set_requires_grad(self, nets, requires_grad=False):
        """Set requies_grad=Fasle for all the networks to avoid unnecessary computations
        Parameters:
            nets (network list)   -- a list of networks
            requires_grad (bool)  -- whether the networks require gradients or not
        """
        if not isinstance(nets, list):
            nets = [nets]
        for net in nets:
            if net is not None:
                for param in net.parameters():
                    param.requires_grad = requires_grad

    # update learning rate (called once every epoch)
    def update_learning_rate(self):
        for scheduler in self.schedulers:
            scheduler.step()
        lr = self.optimizers[0].param_groups[0]['lr']
        print('[*] learning rate = %.7f' % lr)

    def update_learning_rate_cos(self, epoch, opt):
        """Decay the learning rate with half-cycle cosine after warmup"""
        if epoch >= opt.warmup_epochs:
            lr = opt.min_lr + (opt.lr - opt.min_lr) * 0.5 * \
                (1. + math.cos(math.pi * (epoch - opt.warmup_epochs) / (opt.epochs - opt.warmup_epochs)))
            for param_group in self.optimizer.param_groups:
                if "lr_scale" in param_group:
                    param_group["lr"] = lr * param_group["lr_scale"]
                else:
                    param_group["lr"] = lr
            print('[*] learning rate = %.7f' % lr)

    def eval(self):
        for name in self.model_names:
            if isinstance(name, str):
                net = getattr(self, 'net' + name)
                net.eval()

    def train(self):
        for name in self.model_names:
            if isinstance(name, str):
                net = getattr(self, 'net' + name)
                net.train()

    # print network information
    def print_networks(self, verbose=False):
        print('---------- Networks initialized -------------')
        for name in self.model_names:
            if isinstance(name, str):
                net = getattr(self, 'net' + name)
                num_params = 0
                for param in net.parameters():
                    num_params += param.numel()
                if verbose:
                    print(net)
                print('[Network %s] Total number of parameters : %.3f M' % (name, num_params / 1e6))
        print('-----------------------------------------------')

    def tocuda(self, var_names):
        for name in var_names:
            if isinstance(name, str):
                var = getattr(self, name)
                # setattr(self, name, var.cuda(self.gpu_ids[0], non_blocking=True))
                setattr(self, name, var.cuda(self.opt.device, non_blocking=True))


    def tnsrs2ims(self, tensor_names):
        ims = []
        for name in tensor_names:
            if isinstance(name, str):
                var = getattr(self, name)
                ims.append(util.tensor2im(var.data))
        return ims
