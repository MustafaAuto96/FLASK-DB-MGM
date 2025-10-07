from extensions import db
from models import User

admin = User(username='admin', group='Admin')
admin.set_password('adminpass')
db.session.add(admin)
db.session.commit()
print('Admin user created!')
exit()