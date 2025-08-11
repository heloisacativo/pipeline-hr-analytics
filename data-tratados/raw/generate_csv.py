import pandas as pd
import random
import datetime
import os


n = 200
start_date = datetime.date(2020, 1, 1)
end_date = datetime.date(2023, 12, 31)
departaments = ['RH', 'TI', 'Financeiro', 'Marketing', 'Operações']

def random_date(start, end):
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))

data = []
for i in range(n):
    eid = 1000 + i
    vac_start = random_date(start_date, end_date - datetime.timedelta(days=15))
    vac_end = vac_start + datetime.timedelta(days=random.randint(1, 15))
    absences = random.randint(0, 10)
    status = "ativo" if random.random() > 0.1 else "inativo"
    data.append({
        "employee_id": eid,
        "employee_name": f"Emp{eid}",
        "department": random.choice(departaments),
        "vacation_start": vac_start,
        "vacation_end": vac_end,
        "absences": absences,
        "status": status
    })

df = pd.DataFrame(data)

base_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(base_dir, 'input_large.csv')

os.makedirs(base_dir, exist_ok=True)

df.to_csv(output_path, index=False)
print(f"CSV file generated at {output_path}")