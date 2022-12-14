from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .tensor import Tensor

import numpy as np

indent = 1
print_ok = True


def printed(func):
    if print_ok is False:
        return lambda *args, **kwargs: func(*args, **kwargs)
    import functools

    @functools.wraps(func)
    def p(*args, **kwargs):
        global indent
        print("------------------------------------")
        print(" "*indent, f"called: '{func.__name__}'")
        indent += 1
        res = func(*args, **kwargs)
        indent += -1
        print(" "*indent, f"res   : '{res}'")
        return res
    return p


@printed
def is_scalar(tensor: Tensor) -> bool:
    return np.isscalar(tensor)


@printed
def relu(tensor: Tensor) -> Tensor:
    tensor = tensor.copy()
    tensor[tensor < 0] = 0
    return tensor


@printed
def sigmoid(tensor: Tensor) -> Tensor:
    return 1 / ((-tensor).exp() + 1)


@printed
def softmax(tensor: Tensor, dim: int = 0) -> Tensor:
    # avoids overflow , https://timvieira.github.io/blog/post/2014/02/11/exp-normalize-trick/
    b = tensor.max() or 0
    e = (tensor - b).exp()
    return e/e.sum(axis=dim, keepdims=True)


@printed
def log_softmax(tensor: Tensor, dim=0) -> Tensor:
    return tensor.softmax(dim=dim).log()


@printed
def cross_entropy(x: Tensor, t, dim=0, reduction="none", from_logits=False) -> Tensor:
    # if from_logits:
    #     TODO : from_logits is True
    #     t = t.flatten().astype(np.int32)
    return x.log_softmax(dim).negative_log_likelihood(t, reduction=reduction)


@printed
def negative_log_likelihood(x: Tensor, t, reduction="none") -> Tensor:
    lns_ = []
    for i, _ in enumerate(x):
        # print("a",i,t[i])
        lns_.append(- x[i][t[i]])
    from .tensor import Tensor
    lns = Tensor.array(lns_)
    if reduction in [None, "none"]:
        return lns
    elif reduction == "sum":
        return lns.sum()
    elif reduction == "mean":
        return lns.mean()
    raise Exception(f"Invalid argument {reduction=}")


@printed
def conv2d_output_shape(x: Tensor, out_, ks, p=0, s=1, d=0):
    b, _, w, h = tuple(x.shape)
    s1, s2 = s if isinstance(s, tuple) else (s, s)
    p1, p2 = p if isinstance(p, tuple) else (p, p)
    d1, d2 = d if isinstance(d, tuple) else (d, d)
    ks1, ks2 = ks
    from math import ceil
    # w,h = (w-ks1+p1+s1)/s1,(h-ks2+p2+s2)/s2
    # w = ceil(w) if w - int(w) < .5 else ceil(w)+1
    # h = ceil(h) if h - int(h) < .5 else ceil(h)+1

    w = (w+2*p1-d1*(ks1-1)-1)//s1 + 1
    h = (h+2*p2-d2*(ks2-1)-1)//s2 + 1
    out_shape = b, out_, w, h
    return out_shape


@printed
def linear(a: Tensor, w: Tensor, b: Tensor) -> Tensor:
    """
    returns a*w+b
    """
    assert a.shape[-1] == w.shape[0]
    assert b is None or b.shape[-1] == w.shape[-1]
    return (a @ w).biased(b)


@printed
def biased(x: Tensor, bias: Tensor | None = None) -> Tensor:
    if bias is not None:
        assert tuple(x.shape) == tuple(bias.shape)
        x += bias
    return x


@printed
def sequential(x: Tensor, layers) -> Tensor:
    for layer in layers:
        x = layer(x)
    return x


@printed
def conv2d(x: Tensor, w: Tensor, b: Tensor, padding=0, stride=1, dilation=0):
    pass
