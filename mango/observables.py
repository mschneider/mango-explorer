# # ⚠ Warning
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# [🥭 Mango Markets](https://mango.markets/) support is available at:
#   [Docs](https://docs.mango.markets/)
#   [Discord](https://discord.gg/67jySBhxrg)
#   [Twitter](https://twitter.com/mangomarkets)
#   [Github](https://github.com/blockworks-foundation)
#   [Email](mailto:hello@blockworks.foundation)


import datetime
import logging
import rx
import rx.subject
import typing

from rx.core.abc.disposable import Disposable
from rxpy_backpressure import BackPressure


# # 🥭 Observables
#
# This notebook contains some useful shared tools to work with
# [RX Observables](https://rxpy.readthedocs.io/en/latest/reference_observable.html).
#

# # 🥭 PrintingObserverSubscriber class
#
# This class can subscribe to an `Observable` and print out each item.
#


class PrintingObserverSubscriber(rx.core.typing.Observer):
    def __init__(self, report_no_output: bool) -> None:
        super().__init__()
        self.report_no_output = report_no_output

    def on_next(self, item: typing.Any) -> None:
        self.report_no_output = False
        print(item)

    def on_error(self, ex: Exception) -> None:
        self.report_no_output = False
        print(ex)

    def on_completed(self) -> None:
        if self.report_no_output:
            print("No items to show.")


# # 🥭 TimestampedPrintingObserverSubscriber class
#
# Just like `PrintingObserverSubscriber` but it puts a timestamp on each printout.
#

class TimestampedPrintingObserverSubscriber(PrintingObserverSubscriber):
    def __init__(self, report_no_output: bool) -> None:
        super().__init__(report_no_output)

    def on_next(self, item: typing.Any) -> None:
        super().on_next(f"{datetime.datetime.now()}: {item}")


# # 🥭 CollectingObserverSubscriber class
#
# This class can subscribe to an `Observable` and collect each item.
#


class CollectingObserverSubscriber(rx.core.typing.Observer):
    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.collected: typing.List[typing.Any] = []

    def on_next(self, item: typing.Any) -> None:
        self.collected += [item]

    def on_error(self, ex: Exception) -> None:
        self.logger.error(f"Received error: {ex}")

    def on_completed(self) -> None:
        pass


# # 🥭 CaptureFirstItem class
#
# This captures the first item to pass through the pipeline, allowing it to be instpected
# later.
#


class CaptureFirstItem:
    def __init__(self):
        self.captured: typing.Any = None
        self.has_captured: bool = False

    def capture_if_first(self, item: typing.Any) -> typing.Any:
        if not self.has_captured:
            self.captured = item
            self.has_captured = True

        return item


# # 🥭 FunctionObserver
#
# This class takes functions for `on_next()`, `on_error()` and `on_completed()` and returns
# an `Observer` object.
#
# This is mostly for libraries (like `rxpy_backpressure`) that take observers but not their
# component functions.
#


class FunctionObserver(rx.core.typing.Observer):
    def __init__(self,
                 on_next: typing.Callable[[typing.Any], None],
                 on_error: typing.Callable[[Exception], None] = lambda _: None,
                 on_completed: typing.Callable[[], None] = lambda: None):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self._on_next = on_next
        self._on_error = on_error
        self._on_completed = on_completed

    def on_next(self, value: typing.Any) -> None:
        try:
            self._on_next(value)
        except Exception as exception:
            self.logger.warning(f"on_next callable raised exception: {exception}")

    def on_error(self, error: Exception) -> None:
        try:
            self._on_error(error)
        except Exception as exception:
            self.logger.warning(f"on_error callable raised exception: {exception}")

    def on_completed(self) -> None:
        try:
            self._on_completed()
        except Exception as exception:
            self.logger.warning(f"on_completed callable raised exception: {exception}")


# # 🥭 create_backpressure_skipping_observer function
#
# Creates an `Observer` that skips inputs if they are building up while a subscriber works.
#
# This is useful for situations that, say, poll every second but the operation can sometimes
# take multiple seconds to complete. In that case, the latest item will be immediately
# emitted and the in-between items skipped.
#

def create_backpressure_skipping_observer(on_next: typing.Callable[[typing.Any], None], on_error: typing.Callable[[Exception], None] = lambda _: None, on_completed: typing.Callable[[], None] = lambda: None) -> rx.core.typing.Observer:
    observer = FunctionObserver(on_next=on_next, on_error=on_error, on_completed=on_completed)
    return BackPressure.LATEST(observer)


# # 🥭 debug_print_item function
#
# This is a handy item that can be added to a pipeline to show what is being passed at that particular stage. For example, this shows how to print the item before and after filtering:
# ```
# fetch().pipe(
#     ops.map(debug_print_item("Unfiltered:")),
#     ops.filter(lambda item: item.something is not None),
#     ops.map(debug_print_item("Filtered:")),
#     ops.filter(lambda item: item.something_else()),
#     ops.map(act_on_item)
# ).subscribe(some_subscriber)
# ```
#

def debug_print_item(title: str) -> typing.Callable[[typing.Any], typing.Any]:
    def _debug_print_item(item: typing.Any) -> typing.Any:
        print(title, item)
        return item
    return _debug_print_item


# # 🥭 log_subscription_error function
#
# Logs subscription exceptions to the root logger.
#

def log_subscription_error(error: Exception) -> None:
    logging.error(f"Observable subscription error: {error}")


# # 🥭 observable_pipeline_error_reporter function
#
# This intercepts and re-raises an exception, to help report on errors.
#
# RxPy pipelines are tricky to restart, so it's often easier to use the `ops.retry()`
# function in the pipeline. That just swallows the error though, so there's no way to know
# what was raised to cause the retry.
#
# Enter `observable_pipeline_error_reporter()`! Put it in a `catch` just before the `retry`
# and it should log the error properly.
#
# For example:
# ```
# from rx import of, operators as ops
#
# def raise_on_every_third(item):
#     if (item % 3 == 0):
#         raise Exception("Divisible by 3")
#     else:
#         return item
#
# sub1 = of(1, 2, 3, 4, 5, 6).pipe(
#     ops.map(lambda e : raise_on_every_third(e)),
#     ops.catch(observable_pipeline_error_reporter),
#     ops.retry(3)
# )
# sub1.subscribe(lambda item: print(item), on_error = lambda error: print(f"Error : {error}"))
# ```
#

def observable_pipeline_error_reporter(ex, _):
    logging.error(f"Intercepted error in observable pipeline: {ex}")
    raise ex


# # 🥭 EventSource class
#
# A strongly(ish)-typed event source that can handle many subscribers.
#

TEventDatum = typing.TypeVar('TEventDatum')


class EventSource(rx.subject.Subject, typing.Generic[TEventDatum]):
    def __init__(self) -> None:
        super().__init__()
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

    def on_next(self, event: TEventDatum) -> None:
        super().on_next(event)

    def on_error(self, ex: Exception) -> None:
        super().on_error(ex)

    def on_completed(self) -> None:
        super().on_completed()

    def publish(self, event: TEventDatum) -> None:
        try:
            self.on_next(event)
        except Exception as exception:
            self.logger.warning(f"Failed to publish event '{event}' - {exception}")

    def dispose(self) -> None:
        super().dispose()


# # 🥭 DisposePropagator class
#
# A `Disposable` class that can 'fan out' `dispose()` calls to perform additional
# cleanup actions.
#

class DisposePropagator(Disposable):
    def __init__(self):
        self.handlers: typing.List[typing.Callable[[], None]] = []

    def add_ondispose(self, handler: typing.Callable[[], None]):
        self.handlers += [handler]

    def dispose(self):
        for handler in self.handlers:
            handler()
