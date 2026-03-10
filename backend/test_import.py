# test import
import sys
print("Python path:", sys.path)

try:
    from app.models.customer import Customer
    print("Customer model: OK")
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    from app.models.project import Project
    print("Project model: OK")
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    from app.models.candidate import Candidate
    print("Candidate model: OK")
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    from app.api.customers import router
    print("Customer API: OK")
except Exception as e:
    import traceback
    traceback.print_exc()

print("All imports done!")
