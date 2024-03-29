from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src._tensor import _Tensor
from src.grad.utils import register_grad, _pass_gradient
from src.utils import as_loss_layer, printed_loss


@as_loss_layer("CrossEntropyLoss")
@printed_loss
@register_grad()
def cross_entropy(x: _Tensor, t, dim=-1, reduction="mean") -> _Tensor:
    # if from_logits:
    #     TODO : from_logits is True
    def backward(gradient):
        n, *_ = x.shape
        dx = x.softmax(dim=1)
        dx.data[list(range(n)), t.astype(int)] -= 1
        dx /= n
        _pass_gradient(x, dx * gradient)
    xx = x.log_softmax(dim)
    xx = xx.nll(t, reduction=reduction)
    return xx, backward


@as_loss_layer("NLLLoss")
@printed_loss
@register_grad()
def negative_log_likelihood(x: _Tensor, tt, reduction="mean") -> _Tensor:
    def backward(gradient):
        from src import tensor
        len_ = len(t)
        y = tensor.zeros((x.shape))
        y.data[list(range(len_)), tt.numpy().astype(int)] = -(1/len_)
        _pass_gradient(x, y * gradient)
    from src import tensor
    t = tt.numpy().astype(int)
    y = tensor.zeros((len(t), x.shape[-1]))
    y.data[list(range(len(t))), t] = -1
    res = (x*y).sum(axis=1)
    if reduction == "mean":
        res = res.mean()
    elif reduction == "sum":
        res = res.sum()
    return res, backward


@as_loss_layer("MSELoss")
@printed_loss
@register_grad()
def mse(x: _Tensor, t) -> _Tensor:
    batch_size = x.shape[0]
    raise NotImplementedError()

    def backward(gradient):
        gradient1 = ((1/2*batch_size) * (x-t)).sum(-1, keepdim=True)
        _pass_gradient(x, gradient1*gradient)
    res = ((x - t)**2).sum() / batch_size
    return res, backward
