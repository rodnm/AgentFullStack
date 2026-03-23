import React, { useState } from 'react';

const TodoList = () => {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');

  const addTask = () => {
    if (newTask.trim() !== '') {
      setTasks([...tasks, { id: Date.now(), text: newTask, completed: false }]);
      setNewTask('');
    }
  };

  const toggleTask = (id) => {
    setTasks(
      tasks.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const deleteTask = (id) => {
    setTasks(tasks.filter((task) => task.id !== id));
  };

  return (
    <div className="w-full max-w-md mx-auto bg-win95-bg border-t-win95-border-light border-l-win95-border-light border-b-win95-border-dark border-r-win95-border-dark border-4 shadow-win95">
      <div className="bg-win95-blue text-white p-1 flex items-center">
        <span className="flex-grow ml-2">Lista de Tareas</span>
        <button className="w-6 h-6 bg-win95-button border-t-win95-button-light border-l-win95-button-light border-b-win95-button-dark border-r-win95-button-dark border-2 text-win95-text flex items-center justify-center text-lg leading-none active:shadow-win95-button-active">X</button>
      </div>
      <div className="p-4">
        <div className="flex mb-4 border-t-win95-border-dark border-l-win95-border-dark border-b-win95-border-light border-r-win95-border-light border-2 shadow-win95-inset">
          <input
            type="text"
            className="flex-grow p-1 bg-win95-bg focus:outline-none"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTask()}
            placeholder="Añadir nueva tarea..."
          />
          <button
            onClick={addTask}
            className="ml-2 px-4 py-1 bg-win95-button border-t-win95-button-light border-l-win95-button-light border-b-win95-button-dark border-r-win95-button-dark border-2 active:shadow-win95-button-active"
          >
            Añadir
          </button>
        </div>
        <ul>
          {tasks.map((task) => (
            <li key={task.id} className="flex items-center mb-2">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => toggleTask(task.id)}
                className="mr-2 w-4 h-4 appearance-none border-t-win95-border-dark border-l-win95-border-dark border-b-win95-border-light border-r-win95-border-light border-2 bg-win95-bg checked:bg-win95-blue checked:border-win95-blue"
              />
              <span className={`flex-grow ${task.completed ? 'line-through text-win95-border-dark' : ''}`}>
                {task.text}
              </span>
              <button
                onClick={() => deleteTask(task.id)}
                className="ml-2 px-3 py-1 bg-win95-button border-t-win95-button-light border-l-win95-button-light border-b-win95-button-dark border-r-win95-button-dark border-2 text-sm active:shadow-win95-button-active"
              >
                Eliminar
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TodoList;