# How to add a new model

## Overview
- Make a `torchbenchmark/models` subdir containing the glue code to hook your model into the suite.
- Either copy the model srcs directly, or pip install a pinned version of a library via your model's `requirements.txt`.
- Prepare a single train and eval datum for use with benchmarking.
- (Optional) modify the model to support JIT compilation.

## Detailed steps

### Adding the model code
The intent is to preserve the original user code as much as possible while 
adding support for a standardized interface to the benchmark suite and making sure
the code can run from any directory and in a process with other models.

In many case it is fine to simply copy the entire original repo into a subdirectory
as a starting point, paying attention to avoid the .git folder, and not to add any 
large unnecessary data files unintentionally.  The subdirectory name should be a valid
Python identifier because it will become a module in Python and needs to be importable.

Create a new file 'origin' that contains the url to the git repo you're copying, 
so it's easy to trace the code back to where it came from.

#### Wrapping your model in \_\_init\_\_.py
This is how your model gets hooked up to the suite and discovered by the benchmark and unit test runners.

This file should define a Model class that subclasses from `torchbenchmark.util.model.BenchmarkModel` and implements its APIs.

Some of the APIs are optional, and you can raise NotImplemented if a particular mode (e.g., cuda or jit) is unsupported for your model.

Take care to set the random seed like [here](https://github.com/pytorch/benchmark/blob/master/torchbenchmark/models/Background_Matting/__init__.py#L20), to ensure your model runs the same way each time it's benchmarked.


#### A minimal new model addition
A bare miminum example you can follow is https://github.com/pytorch/benchmark/tree/main/torchbenchmark/models/phlippe_resnet

The functions you specifically need to implement are 
1. `__init__()` which is responsible for initalizing your `nn.Module`
2. `get_module()` which is responsible for returning the initialized `nn.Module` and an example input
3. `train()` which is a training loop, you can return a `NotImplementedError()` if your example is inference only
4. `eval()` which showcases a simple inference

### Preparing install.py and dependencies
Simply put, install.py should be a one stop shop to install all the dependencies
for your model, __except torch, torchvision, torchtext__ which should be assumed to 
have been installed by an outsider (the benchmark CI).

- Avoid pinning packages to specific versions with == without good reason, as the
dependencies for all models get installed into the same environment currently;
- *except* for dependencies that define your model code, such as a library like huggingface, in cases where you did not copy the model source- then you do want to pin with ==, so your model does not silently change from run to run.
- Usually, leverage a requirements.txt and/or the existing `setup.py`.

If the model depends on a C or cuda extension, it may still be possible to invoke
the build steps from install.py.  Avoid getting too fancy trying to be cross-platform
compatible (e.g., Windows/Mac/etc., or using package managers like yum/dnf) - if it's
not easy to build, there may be easier models to target.

[Example install.py](attention_is_all_you_need_pytorch/install.py)

### Mini-dataset
By the time install.py script runs, a miniature version of the dataset is expected to be 
staged and ready for use.  It's fine to use install.py to download and prepare the data
if the download is quick.  Otherwise, prepare the dataset manually, checking in the required
artifacts and modifying the \_\_init\_\_.py script as needed to use them.

- The easiest approach may be to run the dataloader an iteration, pickle its output, and check
that file.
- It's also fine to manually modify the raw data files to include only a small fraction, but make sure not to run the dataloader during train/eval measurements.


### Making the benchmark code run robustly

We want to make it easy to write custom scripts that measure various things about our benchmark code.
Benchmark code should run regardless of the current working directory. It should also clean up all of its
GPU memory when the Model object associated with the run is freed. Our tests scripts will test these properties.
Model code will require some small tweaks to make it work in these conditions:

- switch within-model package imports from absolute imports to relative ones `import utils -> from . import utils`, or
  `from utils import Foo -> from .utils import Foo`
- Make the paths of dataset files relative to the package location. You can do this using the `__file__` attribute of
  the source file that specifies the data set. `str(pathlib.Path(__file__).parent)` is the path to the directory that the source
  file lives in.
- Look for errors in `test.py` tearDown. They might indicate that the model is not cleaning up GPU memory.

### Creating your benchmark/\_\_init\_\_.py
This file should define two things:
- `class Model`, extending `BenchmarkModel` with the API described below
- `__main__` function, which exercises the model APIs for local testing

Important: be deliberate about support for cpu/gpu and jit/no-jit.  In the case that
your model is instantiated in an unsupported configuration, the convention is to return
a model object from \_\_init\_\_ but raise NotImplementedError() from all its methods.

See the [BenchmarkModel API](https://github.com/pytorch/benchmark/blob/master/torchbenchmark/util/model.py) to get started. The [attention is all you need](attention_is_all_you_need_pytorch/__init__.py) benchmark can serve as a good example.

### JIT
As an optional step, make whatever modifications necessary to the model code to enable it to script or trace.  If doing this,
make sure to verify correctness by capturing the output of the non-jit model for a given seed/input and replicating it with the JIT
version.

[PyTorch Docs: Creating Torchscript Code](https://pytorch.org/docs/1.1.0/jit.html#creating-torchscript-code)

### Test

After you've submitted your new model, suppose it was called `new_model` make sure the tests pass locally. Your model name is equivalent to the new folder you'd have created in `torchbenchmark/models`

1. `cd benchmark`
2. `python install.py`
3. `python test.py -k "test_new_model"`

And thank you for contributing to torchbench!
