from __future__ import annotations
import numpy as np


class _Tensor:
    from src import nn
    import src.ops as ops

    _is_leaf = True
    _grad = None
    grad_fn:  None = None
    requires_grad = False

    def __init__(self, data: np.ndarray) -> None:
        super().__init__()
        self._init()
        self.data = data
        self.name = ""
        self._backward = None

    def requires_grad_(self, requires_grad=True):
        if requires_grad and self.requires_grad != requires_grad:
            def accumulate_backward(grad):
                self._accumulate_grad(grad)
            accumulate_backward._fn_name = "AccumulateBackward"
            self._backward = accumulate_backward
        self.requires_grad = requires_grad
        return self

    def set_grad_fn(self, grad_fn):
        assert self.grad_fn is None, f"{self.grad_fn.__class__.__name__} --> {grad_fn.__class__.__name__}"
        self.grad_fn = grad_fn

    @property
    def grad(self) -> _Tensor: return self._grad
    @property
    def shape(self) -> _Tensor: return self.data.shape
    @property
    def size(self) -> _Tensor: return self.data.size
    @property
    def dtype(self) -> _Tensor: return self.data.dtype

    @property
    def T(self) -> _Tensor:
        # TODO: make it use np.transpose()
        copy = self.copy()
        copy.data = copy.data.T
        return copy

    def copy(self):
        # TODO: might be wrong
        copy = tensor.from_numpy(
            self.data.copy()).requires_grad_(self.requires_grad)
        return copy

    def _accumulate_grad(self, gradient):
        assert self.requires_grad
        grad = self.grad
        if grad is None:
            grad = tensor.from_numpy(0)
        grad = grad + gradient
        self.set_grad(grad)

    def set_grad(self, grad):
        assert isinstance(grad, _Tensor)
        self_shape, grad_shape = tuple(self.shape), tuple(grad.shape)
        assert self_shape == grad_shape, f"Expected gradient of shape: {self_shape},recieved: {grad_shape}"
        self._grad = grad

    def zero_grad(self):
        # self._grad *=0
        if self._grad is not None:
            self.set_grad(tensor.zeros_like(self._grad))

    def _init(self):
        self._is_leaf = True
        self._grad = None
        self.grad_fn = None

    def float(self):
        self.data = self.data.astype(float)
        return self

    def astype(self, type):
        self.data = self.data.astype(type)
        return self

    @classmethod
    def array(cls, arr: _Tensor | np.ndarray | list, dtype=np.float32) -> _Tensor:
        arr = np.array(arr, dtype=dtype)
        arr = cls(arr)
        arr._init()
        return arr

    @staticmethod
    def ns_like(x, n): return tensor.ns(x.shape, n)
    @staticmethod
    def zeros_like(x): return tensor.ns_like(x, 0)
    @staticmethod
    def ones_like(x): return tensor.ns_like(x, 1)
    @staticmethod
    def ns(shape, k): return tensor.from_numpy(np.zeros(shape)+k)
    @staticmethod
    def ones(shape): return tensor.ns(shape, 1)
    @staticmethod
    def zeros(shape): return tensor.ns(shape, 0)

    # def numpy(self): return np.add(self.data, 0)
    def numpy(self): return self.data

    def to_numpy(self, *args):
        return self.data.copy()

    def is_a_leaf(self): return self._is_leaf

    def can_calculatebackward(self):
        if self._backward is None:
            return False
        return True

    def backward(self, gradient=1):
        if not isinstance(gradient, _Tensor):
            gradient = tensor.from_numpy(gradient)
        assert self.can_calculatebackward()
        # TODO
        # assert np.isfinite(self.data), f"Value is infinite: {self.data}"
        if self._backward._fn_name != "AccumulateBackward":
            self._accumulate_grad(gradient)
        self._backward(gradient)

    def is_scalar(self):
        # return np.isscalar(self)
        return self.shape == ()

    __add__ = ops.add
    __sub__ = ops.sub
    __mul__ = ops.mul
    __pow__ = ops.pow
    __div__ = ops.truediv
    __truediv__ = ops.truediv
    __rtruediv__ = ops.rtruediv
    __matmul__ = ops.matmul
    __neg__ = ops.neg

    __rmul__ = __mul__
    __radd__ = __add__
    __rsub__ = __sub__
    __iadd__ = __add__
    __isub__ = __sub__
    __imul__ = __mul__

    mean = ops.mean
    sum = ops.sum
    log = ops.log
    exp = ops.exp

    # ------------activations--------------
    tanh = nn.activation.tanh
    relu = nn.activation.relu
    sigmoid = nn.activation.sigmoid
    softmax = nn.activation.softmax
    log_softmax = nn.activation.log_softmax
    # ------------loss--------------
    mse = nn.loss.mse
    cross_entropy = nn.loss.cross_entropy
    nll = nn.loss.negative_log_likelihood
    # ------------ops--------------
    biased = ops.biased
    linear = ops.linear
    conv2d = ops.conv2d
    dropout = ops.dropout
    flatten = ops.flatten
    reshape = ops.reshape
    squeeze = ops.squeeze
    unsqueeze = ops.unsqueeze
    sequential = ops.sequential

    def __len__(self):
        return self.data.__len__()
    # ------------$--------------
    unique = lambda self, *args, **kwargs: np.unique(self, *args, **kwargs)

    # NOTE: For tests
    def detach(self): return self

    def torch(self):
        import torch
        return torch.from_numpy(self.numpy()).requires_grad_(self.requires_grad)

    def __repr__(self) -> str:
        v = (
            # f".val          = {self.numpy()}",
            f".requires_grad= {self.requires_grad}",
            f".grad_fn      = {type(self.grad_fn).__name__}"
        )
        t = "\n".join(v)
        return f'<nn.Tensor\n{t}/>'

    def __str__(self) -> str:
        return str(self.numpy())

    # def __getattr__(self, f):
    #     copy = self.copy()
    #     func = getattr(np, f)
    #     copy.data = func()
    @classmethod
    def rand(cls, *args): return tensor.from_numpy(np.random.rand(*args))

    @classmethod
    def uniform(cls, shape, low=0, high=1): return tensor.from_numpy(
        np.random.uniform(low, high, shape))

    def argmax(self, *args):
        return tensor.from_numpy(self.data.argmax(*args)).requires_grad_()

    __getitem__ = ops.select
    __setitem__ = ops.copy_slice
    __array__ = to_numpy


class tensor:
    tensor = _Tensor.array
    from_numpy = tensor
    zeros = _Tensor.zeros
    zeros_like = _Tensor.zeros_like
    ones = _Tensor.ones
    ones_like = _Tensor.ones_like
    ns_like = _Tensor.ns_like
    ns = _Tensor.ns
