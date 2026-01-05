import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsAPI } from '../lib/api';

function Projects() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({ name: '', bot_token: '', admin_id: '' });
    const [error, setError] = useState('');

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            const response = await projectsAPI.getAll();
            setProjects(response.data);
        } catch (error) {
            console.error('Failed to load projects:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        setError('');

        try {
            await projectsAPI.create({
                ...formData,
                admin_id: parseInt(formData.admin_id) || 0
            });
            setFormData({ name: '', bot_token: '', admin_id: '' });
            setShowModal(false);
            loadProjects();
        } catch (error) {
            setError(error.response?.data?.detail || 'Ошибка создания проекта');
        }
    };

    const handleDelete = async (id, e) => {
        e.stopPropagation();
        if (!confirm('Удалить проект?')) return;

        try {
            await projectsAPI.delete(id);
            loadProjects();
        } catch (error) {
            console.error('Failed to delete project:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen gradient-bg flex items-center justify-center">
                <div className="text-xl text-gray-400">Загрузка...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen gradient-bg p-8">
            {/* Header */}
            <div className="max-w-6xl mx-auto">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                            TG-Otvet
                        </h1>
                        <p className="text-gray-400 mt-2">Система управления Telegram-ботами</p>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <span>+</span>
                        <span>Создать проект</span>
                    </button>
                </div>

                {/* Projects grid */}
                {projects.length === 0 ? (
                    <div className="text-center py-20">
                        <div className="text-6xl mb-4">🤖</div>
                        <h2 className="text-2xl font-semibold text-gray-300 mb-2">Нет проектов</h2>
                        <p className="text-gray-500 mb-6">Создайте первый проект для начала работы</p>
                        <button
                            onClick={() => setShowModal(true)}
                            className="btn-primary"
                        >
                            Создать проект
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
                        {projects.map(project => (
                            <div
                                key={project.id}
                                onClick={() => navigate(`/project/${project.id}/users`)}
                                className="card cursor-pointer group"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-2xl">
                                        🤖
                                    </div>
                                    <button
                                        onClick={(e) => handleDelete(project.id, e)}
                                        className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-all"
                                        title="Удалить"
                                    >
                                        🗑️
                                    </button>
                                </div>
                                <h3 className="text-xl font-semibold text-white mb-2">{project.name}</h3>
                                <p className="text-sm text-gray-500 truncate font-mono">
                                    {project.bot_token.slice(0, 20)}...
                                </p>
                                <div className="mt-4 pt-4 border-t border-gray-700/50 text-xs text-gray-500">
                                    Создан: {new Date(project.created_at).toLocaleDateString('ru-RU')}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Create Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content animate-fade-in" onClick={e => e.stopPropagation()}>
                        <h2 className="text-2xl font-bold text-white mb-6">Новый проект</h2>

                        {error && (
                            <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-4">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleCreate}>
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Название проекта</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="input"
                                    placeholder="Мой бот"
                                    required
                                />
                            </div>

                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Токен бота</label>
                                <input
                                    type="text"
                                    value={formData.bot_token}
                                    onChange={(e) => setFormData({ ...formData, bot_token: e.target.value })}
                                    className="input font-mono text-sm"
                                    placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                                    required
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Получите токен у @BotFather в Telegram
                                </p>
                            </div>

                            <div className="mb-6">
                                <label className="block text-gray-300 mb-2">ID администратора</label>
                                <input
                                    type="number"
                                    value={formData.admin_id}
                                    onChange={(e) => setFormData({ ...formData, admin_id: e.target.value })}
                                    className="input font-mono text-sm"
                                    placeholder="123456789"
                                    required
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Ваш Telegram ID (узнайте у @userinfobot)
                                </p>
                            </div>

                            <div className="flex gap-3">
                                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">
                                    Отмена
                                </button>
                                <button type="submit" className="btn-primary flex-1">
                                    Создать
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Projects;
