import tensorrt as trt
from torch2trt.torch2trt import *
from torch2trt.module_test import add_module_test
from .flatten import *
from .topk import *
from .squeeze import *


@tensorrt_converter('torch.Tensor.argmin')
@tensorrt_converter('torch.argmin')
def convert_argmin(ctx):
    
    old_args = ctx.method_args
    input = ctx.method_args[0]
    dim = get_arg(ctx, 'dim', pos=1, default=None)
    keepdim = get_arg(ctx, 'keepdim', pos=2, default=False)

    output = ctx.method_return

    # dim is None
    if dim is None:
        input_flatten = input.flatten()
        ctx.method_args = [input]
        ctx.method_return = input_flatten
        convert_flatten(ctx)
        input = ctx.method_return
        dim = 0
    
    # topk
    topk_output = input.topk(1, dim, largest=False)
    topk_input = [input, 1, dim, False]
    ctx.method_args = topk_input
    ctx.method_return = topk_output
    convert_topk(ctx)
    topk_index = ctx.method_return[1]


    output._trt = topk_index._trt
    ctx.method_return = output

    # keepdim
    if not keepdim and topk_index.shape[dim]==1 and len(topk_index.shape)>1:
        ctx.method_args = [topk_index, dim]
        ctx.method_return = output
        convert_squeeze(ctx)
    ctx.method_args = old_args

