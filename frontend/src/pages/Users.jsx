import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { usersAPI } from '../lib/api';

function Users() {
    const { projectId } = useOutletContext();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (projectId) loadUsers();
    }, [projectId]);

    const loadUsers = async () => {
        try {
            const response = await usersAPI.getByProject(projectId);
            setUsers(response.data);
        } catch (error) {
            console.error('Failed to load users:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleStatus = async (user) => {
        const newStatus = user.status === 'ACTIVE' ? 'BLOCKED' : 'ACTIVE';
        try {
            await usersAPI.updateStatus(user.id, newStatus);
            loadUsers();
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Удалить пользователя?')) return;
        try {
            await usersAPI.delete(id);
            loadUsers();
        } catch (error) {
            console.error('Failed to delete user:', error);
        }
    };

    if (loading) {
        return <div className="text-center text-gray-400 py-20">Загрузка...</div>;
    }

    return (
        <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-white">Пользователи</h1>
                    <p className="text-gray-400 mt-1">Всего: {users.length}</p>
                </div>
                <button onClick={loadUsers} className="btn-secondary">
                    🔄 Обновить
                </button>
            </div>

            {users.length === 0 ? (
                <div className="text-center py-20">
                    <div className="text-6xl mb-4">👥</div>
                    <h2 className="text-xl text-gray-300 mb-2">Нет пользователей</h2>
                    <p className="text-gray-500">Пользователи появятся после запуска бота</p>
                </div>
            ) : (
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Telegram ID</th>
                                <th>Username</th>
                                <th>Имя</th>
                                <th>Шаг</th>
                                <th>Статус</th>
                                <th>Регистрация</th>
                                <th>Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td className="font-mono text-gray-400">{user.id}</td>
                                    <td className="font-mono">{user.telegram_id}</td>
                                    <td>
                                        {user.username ? (
                                            <a
                                                href={`https://t.me/${user.username}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-indigo-400 hover:text-indigo-300"
                                            >
                                                @{user.username}
                                            </a>
                                        ) : (
                                            <span className="text-gray-500">—</span>
                                        )}
                                    </td>
                                    <td>
                                        {user.first_name || ''} {user.last_name || ''}
                                    </td>
                                    <td>
                                        <span className="badge badge-info">
                                            Шаг {user.funnel_step}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`badge ${user.status === 'ACTIVE' ? 'badge-success' : 'badge-danger'}`}>
                                            {user.status === 'ACTIVE' ? 'Активен' : 'Заблокирован'}
                                        </span>
                                    </td>
                                    <td className="text-gray-400 text-sm">
                                        {new Date(user.created_at).toLocaleString('ru-RU')}
                                    </td>
                                    <td>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => toggleStatus(user)}
                                                className={`text-sm px-3 py-1 rounded ${user.status === 'ACTIVE'
                                                        ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
                                                        : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                                                    }`}
                                                title={user.status === 'ACTIVE' ? 'Заблокировать' : 'Разблокировать'}
                                            >
                                                {user.status === 'ACTIVE' ? '🚫' : '✅'}
                                            </button>
                                            <button
                                                onClick={() => handleDelete(user.id)}
                                                className="text-sm px-3 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
                                                title="Удалить"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

export default Users;
