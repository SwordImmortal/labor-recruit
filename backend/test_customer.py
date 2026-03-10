import sys
sys.path.insert(0, '.')

print("Testing Customer model import...")
try:
    from app.models.customer import Customer
    print("SUCCESS: Customer model imported")
    print(f"Customer tablename: {Customer.__tablename__}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
