from stmlearn.equivalencecheckers import WmethodEquivalenceChecker
from stmlearn.learners import LStarMealyLearner
from stmlearn.teachers import Teacher
from stmlearn.suls.caches.dictcache import DictCache

from TLSSUL import TLSSUL
from TLSAttackerMapper import TLSAttackerMapper

# Modify to point to where you put TLSAttacker
tlsattacker_path = '../../tlsattacker/TLS-Attacker/apps/TLS-Client.jar'

sul = TLSSUL(
    TLSAttackerMapper(
        tlsa_path=tlsattacker_path,
        addr='localhost',
        port=4433
    )
)

# Use the W method equivalence checker
eqc = WmethodEquivalenceChecker(sul, m=9)

teacher = Teacher(sul, eqc)

# We are learning a mealy machine
learner = LStarMealyLearner(teacher)

hyp = learner.run(show_intermediate=True)

hyp.render_graph()
