from todoapp import app
from todoapp.models import db, Usuario, Lista, Tarefa

db.create_tables([Usuario, Lista, Tarefa])

if __name__ == '__main__':
    app.run(debug=True)
