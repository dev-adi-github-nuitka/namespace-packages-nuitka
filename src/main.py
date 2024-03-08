import shared_ns
from shared_ns.thing1 import ThingOne
from shared_ns.thing2 import ThingTwo


def run():
    print(ThingOne.name)
    print(ThingTwo.name)
    print(shared_ns.__path__)


if __name__ == "__main__":
    run()