import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { broadcastsAPI, usersAPI, mediaAPI } from '../lib/api';

function Broadcast() {
    const { projectId } = useOutletContext();
    const [broadcasts, setBroadcasts] = useState([]);
    const [mediaFiles, setMediaFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingBroadcast, setEditingBroadcast] = useState(null);
    const [usersCount, setUsersCount] = useState(0);
    const [activeUsersCount, setActiveUsersCount] = useState(0);

    const [formData, setFormData] = useState({
        name: '',
        content_text: '',
        content_type: 'text',
        media_file_ids: [],
        target_audience: 'all',
        schedule_type: 'now',
        scheduled_at: ''
    });

    useEffect(() => {
        if (projectId) {
            loadBroadcasts();
            loadUsersCounts();
            loadMedia();
        }
    }, [projectId]);

    const loadBroadcasts = async () => {
        try {
            const response = await broadcastsAPI.getByProject(projectId);
            setBroadcasts(response.data);
        } catch (error) {
            console.error('Failed to load broadcasts:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadUsersCounts = async () => {
        try {
            const response = await usersAPI.getByProject(projectId);
            setUsersCount(response.data.length);
            setActiveUsersCount(response.data.filter(u => u.status === 'ACTIVE').length);
        } catch (error) {
            console.error('Failed to load users count:', error);
        }
    };

    const loadMedia = async () => {
        try {
            const response = await mediaAPI.getByProject(projectId);
            setMediaFiles(response.data);
        } catch (error) {
            console.error('Failed to load media:', error);
        }
    };

    const handleFileUpload = async (e) => {
        const files = e.target.files;
        for (const file of files) {
            try {
                await mediaAPI.upload(projectId, file);
            } catch (error) {
                console.error('Failed to upload file:', error);
            }
        }
        loadMedia();
        e.target.value = '';
    };

    const handleSave = async (e) => {
        e.preventDefault();

        try {
            const data = {
                project_id: projectId,
                name: formData.name,
                content_text: formData.content_text || null,
                content_type: formData.content_type,
                media_file_ids: formData.media_file_ids,
                target_audience: formData.target_audience,
                scheduled_at: formData.schedule_type === 'scheduled' && formData.scheduled_at
                    ? new Date(formData.scheduled_at).toISOString()
                    : null
            };

            if (editingBroadcast) {
                await broadcastsAPI.update(editingBroadcast.id, data);
            } else {
                await broadcastsAPI.create(data);
            }

            setShowModal(false);
            setEditingBroadcast(null);
            setFormData({
                name: '',
                content_text: '',
                content_type: 'text',
                media_file_ids: [],
                target_audience: 'all',
                schedule_type: 'now',
                scheduled_at: ''
            });
            loadBroadcasts();
        } catch (error) {
            console.error('Failed to save broadcast:', error);
            alert(error.response?.data?.detail || 'Ошибка сохранения рассылки');
        }
    };

    const handleStart = async (id) => {
        if (!confirm('Запустить рассылку сейчас?')) return;

        try {
            await broadcastsAPI.start(id);
            loadBroadcasts();
            alert('Рассылка запущена!');
        } catch (error) {
            console.error('Failed to start broadcast:', error);
            alert(error.response?.data?.detail || 'Ошибка запуска рассылки');
        }
    };

    const openEdit = (broadcast) => {
        setEditingBroadcast(broadcast);
        setFormData({
            name: broadcast.name,
            content_text: broadcast.content_text || '',
            content_type: broadcast.content_type,
            media_file_ids: broadcast.media_files ? broadcast.media_files.map(m => m.id) : [],
            target_audience: broadcast.target_audience,
            schedule_type: broadcast.scheduled_at ? 'scheduled' : 'now',
            scheduled_at: broadcast.scheduled_at ? new Date(broadcast.scheduled_at).toISOString().slice(0, 16) : ''
        });
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!confirm('Удалить рассылку?')) return;

        try {
            await broadcastsAPI.delete(id);
            loadBroadcasts();
        } catch (error) {
            console.error('Failed to delete broadcast:', error);
        }
    };

    const getStatusBadge = (status) => {
        const badges = {
            draft: { class: 'badge-warning', text: 'Черновик' },
            scheduled: { class: 'badge-info', text: 'Запланирована' },
            sending: { class: 'badge-success', text: 'Отправляется' },
            completed: { class: 'badge-success', text: 'Завершена' },
            failed: { class: 'bg-red-500/20 text-red-400', text: 'Ошибка' }
        };
        const badge = badges[status] || badges.draft;
        return <span className={`badge ${badge.class}`}>{badge.text}</span>;
    };

    const getContentTypeIcon = (type) => {
        const icons = { text: '📝', photo: '🖼️', video: '🎬' };
        return icons[type] || '📝';
    };

    if (loading) {
        return <div className="text-center text-gray-400 py-20">Загрузка...</div>;
    }

    return (
        <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-white">Рассылки</h1>
                    <p className="text-gray-400 mt-1">
                        Получателей: {usersCount} (активных: {activeUsersCount})
                    </p>
                </div>
                <button onClick={() => setShowModal(true)} className="btn-primary">
                    + Новая рассылка
                </button>
            </div>

            {/* Stats cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="card">
                    <div className="text-3xl font-bold text-indigo-400">{broadcasts.length}</div>
                    <div className="text-gray-400 text-sm mt-1">Всего рассылок</div>
                </div>
                <div className="card">
                    <div className="text-3xl font-bold text-green-400">
                        {broadcasts.filter(b => b.status === 'completed').length}
                    </div>
                    <div className="text-gray-400 text-sm mt-1">Завершено</div>
                </div>
                <div className="card">
                    <div className="text-3xl font-bold text-yellow-400">
                        {broadcasts.filter(b => b.status === 'draft').length}
                    </div>
                    <div className="text-gray-400 text-sm mt-1">Черновиков</div>
                </div>
            </div>

            {/* Broadcasts list */}
            {broadcasts.length === 0 ? (
                <div className="text-center py-20">
                    <div className="text-6xl mb-4">📢</div>
                    <h2 className="text-xl text-gray-300 mb-2">Нет рассылок</h2>
                    <p className="text-gray-500 mb-6">Создайте первую рассылку</p>
                    <button onClick={() => setShowModal(true)} className="btn-primary">
                        Создать рассылку
                    </button>
                </div>
            ) : (
                <div className="space-y-4">
                    {broadcasts.map(broadcast => (
                        <div key={broadcast.id} className="card">
                            <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="text-lg font-semibold text-white">{broadcast.name}</h3>
                                        {getStatusBadge(broadcast.status)}
                                    </div>

                                    <p className="text-gray-400 line-clamp-2 mb-3">
                                        {broadcast.content_text || 'Без текста'}
                                    </p>

                                    <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                                        <span>{getContentTypeIcon(broadcast.content_type)} {broadcast.content_type === 'text' ? 'Текст' : broadcast.content_type === 'photo' ? 'Фото' : broadcast.content_type === 'video' ? 'Видео' : 'Альбом'}</span>
                                        <span>
                                            👥 {broadcast.target_audience === 'all' ? 'Все' : 'Активные'}
                                        </span>
                                        {broadcast.sent_count > 0 && (
                                            <span>✅ Отправлено: {broadcast.sent_count}</span>
                                        )}
                                        {broadcast.scheduled_at && (
                                            <span>
                                                📅 {new Date(broadcast.scheduled_at).toLocaleString('ru-RU')}
                                            </span>
                                        )}
                                    </div>
                                </div>

                                <div className="flex gap-2 ml-4">
                                    {broadcast.status === 'draft' && (
                                        <>
                                            <button
                                                onClick={() => handleStart(broadcast.id)}
                                                className="btn-primary text-sm"
                                            >
                                                🚀 Отправить
                                            </button>
                                            <button
                                                onClick={() => openEdit(broadcast)}
                                                className="text-sm px-3 py-2 rounded bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30"
                                            >
                                                ✏️
                                            </button>
                                        </>
                                    )}
                                    <button
                                        onClick={() => handleDelete(broadcast.id)}
                                        className="text-sm px-3 py-2 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Create Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content max-w-xl animate-fade-in max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
                        <h2 className="text-2xl font-bold text-white mb-6">
                            {editingBroadcast ? 'Редактировать рассылку' : 'Новая рассылка'}
                        </h2>

                        <form onSubmit={handleSave}>
                            {/* Name */}
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Название</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="input"
                                    placeholder="Новогодняя акция"
                                    required
                                />
                            </div>

                            {/* Content type */}
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Тип контента</label>
                                <select
                                    value={formData.content_type}
                                    onChange={(e) => setFormData({ ...formData, content_type: e.target.value, media_file_ids: [] })}
                                    className="select"
                                >
                                    <option value="text">📝 Только текст</option>
                                    <option value="photo">🖼️ Фото + текст</option>
                                    <option value="video">🎬 Видео + текст</option>
                                    <option value="album">📷 Альбом + текст</option>
                                </select>
                            </div>

                            {/* Media selection */}
                            {formData.content_type !== 'text' && (
                                <div className="mb-4">
                                    <label className="block text-gray-300 mb-2">
                                        Выберите медиа ({formData.media_file_ids.length} выбрано)
                                    </label>

                                    <div className="flex gap-2 mb-3">
                                        <input
                                            type="file"
                                            id="broadcast-upload"
                                            multiple
                                            accept="image/*,video/*"
                                            onChange={handleFileUpload}
                                            className="hidden"
                                        />
                                        <label htmlFor="broadcast-upload" className="btn-secondary cursor-pointer text-sm">
                                            📤 Загрузить
                                        </label>
                                    </div>

                                    {mediaFiles.length > 0 ? (
                                        <div className="grid grid-cols-4 gap-2 max-h-32 overflow-y-auto p-2 bg-gray-800/50 rounded-lg">
                                            {mediaFiles
                                                .filter(m => formData.content_type === 'album' || m.file_type === formData.content_type)
                                                .map(media => (
                                                    <div
                                                        key={media.id}
                                                        onClick={() => {
                                                            const isSelected = formData.media_file_ids.includes(media.id);
                                                            if (formData.content_type === 'album') {
                                                                setFormData({
                                                                    ...formData,
                                                                    media_file_ids: isSelected
                                                                        ? formData.media_file_ids.filter(id => id !== media.id)
                                                                        : [...formData.media_file_ids, media.id]
                                                                });
                                                            } else {
                                                                setFormData({ ...formData, media_file_ids: [media.id] });
                                                            }
                                                        }}
                                                        className={`relative aspect-square rounded-lg overflow-hidden cursor-pointer border-2 transition-all ${formData.media_file_ids.includes(media.id)
                                                            ? 'border-indigo-500 ring-2 ring-indigo-500/50'
                                                            : 'border-transparent hover:border-gray-500'
                                                            }`}
                                                    >
                                                        {media.file_type === 'photo' ? (
                                                            <img
                                                                src={mediaAPI.getFileUrl(projectId, media.filename)}
                                                                alt=""
                                                                className="w-full h-full object-cover"
                                                            />
                                                        ) : (
                                                            <video
                                                                src={mediaAPI.getFileUrl(projectId, media.filename)}
                                                                className="w-full h-full object-cover"
                                                            />
                                                        )}
                                                        {formData.media_file_ids.includes(media.id) && (
                                                            <div className="absolute top-0.5 right-0.5 w-5 h-5 bg-indigo-500 rounded-full flex items-center justify-center text-xs">
                                                                ✓
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-4 text-gray-500 bg-gray-800/50 rounded-lg text-sm">
                                            Нет файлов. Загрузите медиа.
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Content text */}
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">
                                    Текст сообщения {formData.content_type !== 'text' && '(опционально)'}
                                </label>
                                <textarea
                                    value={formData.content_text}
                                    onChange={(e) => setFormData({ ...formData, content_text: e.target.value })}
                                    className="textarea h-24"
                                    placeholder="Введите текст рассылки..."
                                    required={formData.content_type === 'text'}
                                />
                            </div>

                            {/* Audience */}
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Аудитория</label>
                                <select
                                    value={formData.target_audience}
                                    onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                                    className="select"
                                >
                                    <option value="all">👥 Все пользователи ({usersCount})</option>
                                    <option value="active">✅ Только активные ({activeUsersCount})</option>
                                </select>
                            </div>

                            {/* Schedule */}
                            <div className="mb-6">
                                <label className="block text-gray-300 mb-2">Время отправки</label>
                                <div className="flex gap-4 mb-3">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="schedule"
                                            value="now"
                                            checked={formData.schedule_type === 'now'}
                                            onChange={() => setFormData({ ...formData, schedule_type: 'now', scheduled_at: '' })}
                                            className="text-indigo-500"
                                        />
                                        <span className="text-gray-300">Сейчас</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="schedule"
                                            value="scheduled"
                                            checked={formData.schedule_type === 'scheduled'}
                                            onChange={() => setFormData({ ...formData, schedule_type: 'scheduled' })}
                                            className="text-indigo-500"
                                        />
                                        <span className="text-gray-300">Запланировать</span>
                                    </label>
                                </div>

                                {formData.schedule_type === 'scheduled' && (
                                    <input
                                        type="datetime-local"
                                        value={formData.scheduled_at}
                                        onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
                                        className="input"
                                        required
                                    />
                                )}
                            </div>

                            <div className="flex gap-3">
                                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">
                                    Отмена
                                </button>
                                <button type="submit" className="btn-primary flex-1">
                                    {editingBroadcast ? 'Сохранить' : 'Создать'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Broadcast;
