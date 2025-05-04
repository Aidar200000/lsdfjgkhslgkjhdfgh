from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель задачи
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100), default='Без категории')

    def __repr__(self):
        return f'<Task {self.id}: {self.content} - Done: {self.is_done}>'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form['content'].strip()
        task_category = request.form['category'].strip()

        if not task_content:
            return '⚠️ Нельзя добавить пустую задачу'

        new_task = Task(content=task_content, category=task_category or 'Без категории')
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'Ошибка при добавлении задачи: {e}'

    tasks_todo = Task.query.filter_by(is_done=False).order_by(Task.id.desc()).all()
    tasks_done = Task.query.filter_by(is_done=True).order_by(Task.id.desc()).all()
    return render_template('index.html', tasks_todo=tasks_todo, tasks_done=tasks_done)

@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'Ошибка при удалении задачи: {e}'

@app.route('/toggle/<int:id>')
def toggle_done(id):
    task = Task.query.get_or_404(id)
    task.is_done = not task.is_done
    try:
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'Ошибка при обновлении статуса: {e}'

@app.route('/clear')
def clear_tasks():
    try:
        db.session.query(Task).delete()
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'Ошибка при удалении всех задач: {e}'

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('tasks.db'):
            db.create_all()
        else:
            # Обновление базы вручную: добавить столбцы, если их не было
            with db.engine.connect() as connection:
                try:
                    connection.execute('ALTER TABLE task ADD COLUMN is_done BOOLEAN DEFAULT 0')
                except:
                    pass
                try:
                    connection.execute("ALTER TABLE task ADD COLUMN category VARCHAR(100) DEFAULT 'Без категории'")
                except:
                    pass
        app.run(debug=True)