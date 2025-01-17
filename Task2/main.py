from stmlearn.equivalencecheckers import WmethodEquivalenceChecker
from stmlearn.learners import LStarMealyLearner
from stmlearn.teachers import Teacher
from stmlearn.suls.caches.dictcache import DictCache
from RemoteCoffeeMachineSUL import RemoteCoffeeMachineSUL

# Connection settings
buggy = False

if buggy:
    host = '188.166.11.248'
    port = 31338
    M = 5
else:
    host = '188.166.11.248'
    port = 31337
    M = 10

# Since our queries go over the network,
# they are relatively expensive.
# Thus, it is worthwile to cache them.
sul = DictCache(
    storagepath='cache',
    sul=RemoteCoffeeMachineSUL(host, port),
    saveinterval=1
)

# Use the W method equivalence checker
eqc = WmethodEquivalenceChecker(sul, m=M)
teacher = Teacher(sul, eqc)

# We are learning a mealy machine using L*
learner = LStarMealyLearner(teacher)

hyp = learner.run(show_intermediate=False)
hyp.render_graph()