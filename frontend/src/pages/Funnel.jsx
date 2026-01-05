import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { funnelAPI, mediaAPI } from '../lib/api';

function Funnel() {
    const { projectId } = useOutletContext();
    const [steps, setSteps] = useState([]);
    const [mediaFiles, setMediaFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingStep, setEditingStep] = useState(null);
    const [showMediaModal, setShowMediaModal] = useState(false);

    const [formData, setFormData] = useState({
        step_number: 1,
        delay_value: 0,
        delay_unit: 'seconds',
        content_type: 'text',
        content_text: '',
        media_file_ids: [],
        buttons: []
    });

    useEffect(() => {
        if (projectId) {
            loadSteps();
            loadMedia();
        }
    }, [projectId]);

    const loadSteps = async () => {
        try {
            const response = await funnelAPI.getSteps(projectId);
            setSteps(response.data);
        } catch (error) {
            console.error('Failed to load steps:', error);
        } finally {
            setLoading(false);
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

    const calculateDelaySeconds = (value, unit) => {
        const multipliers = {
            seconds: 1,
            minutes: 60,
            hours: 3600,
            days: 86400
        };
        return value * (multipliers[unit] || 1);
    };

    const formatDelay = (seconds) => {
        if (seconds >= 86400) return `${Math.floor(seconds / 86400)} дн.`;
        if (seconds >= 3600) return `${Math.floor(seconds / 3600)} ч.`;
        if (seconds >= 60) return `${Math.floor(seconds / 60)} мин.`;
        return `${seconds} сек.`;
    };

    const openCreate = () => {
        const nextStep = steps.length > 0 ? Math.max(...steps.map(s => s.step_number)) + 1 : 1;
        setFormData({
            step_number: nextStep,
            delay_value: 0,
            delay_unit: 'seconds',
            content_type: 'text',
            content_text: '',
            media_file_ids: [],
            buttons: []
        });
        setEditingStep(null);
        setShowModal(true);
    };

    const openEdit = (step) => {
        let delay_value = step.delay_seconds;
        let delay_unit = 'seconds';

        if (delay_value >= 86400 && delay_value % 86400 === 0) {
            delay_value = delay_value / 86400;
            delay_unit = 'days';
        } else if (delay_value >= 3600 && delay_value % 3600 === 0) {
            delay_value = delay_value / 3600;
            delay_unit = 'hours';
        } else if (delay_value >= 60 && delay_value % 60 === 0) {
            delay_value = delay_value / 60;
            delay_unit = 'minutes';
        }

        setFormData({
            step_number: step.step_number,
            delay_value,
            delay_unit,
            content_type: step.content_type,
            content_text: step.content_text || '',
            media_file_ids: step.media_files ? step.media_files.map(m => m.id) : [],
            buttons: step.buttons || []
        });
        setEditingStep(step);
        setShowModal(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const delay_seconds = calculateDelaySeconds(formData.delay_value, formData.delay_unit);

        // Filter out empty buttons and format properly
        const validButtons = formData.buttons
            .filter(btn => btn.text && btn.text.trim() !== '')
            .map(btn => ({
                text: btn.text.trim(),
                action: btn.action,
                value: btn.value || '',
                row: 0
            }));

        try {
            const data = {
                delay_seconds,
                content_type: formData.content_type,
                content_text: formData.content_text || '',
                media_file_ids: formData.media_file_ids,
                buttons: validButtons.length > 0 ? validButtons : null
            };

            if (editingStep) {
                await funnelAPI.updateStep(editingStep.id, data);
            } else {
                await funnelAPI.createStep({
                    project_id: projectId,
                    step_number: formData.step_number,
                    ...data
                });
            }
            setShowModal(false);
            loadSteps();
        } catch (error) {
            console.error('Failed to save step:', error);
            alert(error.response?.data?.detail || 'Ошибка сохранения');
        }
    };

    const handleDelete = async (stepId) => {
        if (!confirm('Удалить шаг воронки?')) return;
        try {
            await funnelAPI.deleteStep(stepId, projectId);
            loadSteps();
        } catch (error) {
            console.error('Failed to delete step:', error);
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

    const toggleMediaSelection = (mediaId) => {
        setFormData(prev => ({
            ...prev,
            media_file_ids: prev.media_file_ids.includes(mediaId)
                ? prev.media_file_ids.filter(id => id !== mediaId)
                : [...prev.media_file_ids, mediaId]
        }));
    };

    const handleDeleteMedia = async (mediaId) => {
        if (!confirm('Удалить файл?')) return;
        try {
            await mediaAPI.delete(mediaId);
            loadMedia();
            setFormData(prev => ({
                ...prev,
                media_file_ids: prev.media_file_ids.filter(id => id !== mediaId)
            }));
        } catch (error) {
            console.error('Failed to delete media:', error);
        }
    };

    // Button management - simplified
    const addButton = () => {
        setFormData(prev => ({
            ...prev,
            buttons: [...prev.buttons, { text: '', action: 'url', value: '', row: 0 }]
        }));
    };

    const updateButton = (index, field, value) => {
        setFormData(prev => ({
            ...prev,
            buttons: prev.buttons.map((btn, i) =>
                i === index ? { ...btn, [field]: value } : btn
            )
        }));
    };

    const removeButton = (index) => {
        setFormData(prev => ({
            ...prev,
            buttons: prev.buttons.filter((_, i) => i !== index)
        }));
    };

    if (loading) {
        return <div className="text-center text-gray-400 py-20">Загрузка...</div>;
    }

    return (
        <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-white">Воронка сообщений</h1>
                    <p className="text-gray-400 mt-1">Шагов: {steps.length}</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={() => setShowMediaModal(true)} className="btn-secondary">
                        🖼️ Медиа ({mediaFiles.length})
                    </button>
                    <button onClick={openCreate} className="btn-primary">
                        + Добавить шаг
                    </button>
                </div>
            </div>

            {/* Steps list */}
            {steps.length === 0 ? (
                <div className="text-center py-20">
                    <div className="text-6xl mb-4">🔄</div>
                    <h2 className="text-xl text-gray-300 mb-2">Воронка пуста</h2>
                    <p className="text-gray-500 mb-6">Добавьте первый шаг воронки</p>
                    <button onClick={openCreate} className="btn-primary">
                        Добавить шаг
                    </button>
                </div>
            ) : (
                <div className="space-y-4">
                    {steps.map((step) => (
                        <div key={step.id} className="card flex items-start gap-4">
                            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xl font-bold">
                                {step.step_number}
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-3 mb-2 flex-wrap">
                                    <span className={`badge ${step.content_type === 'text' ? 'badge-info' :
                                        step.content_type === 'photo' ? 'badge-success' :
                                            step.content_type === 'video' ? 'badge-warning' : 'badge-info'
                                        }`}>
                                        {step.content_type === 'text' ? '📝 Текст' :
                                            step.content_type === 'photo' ? '🖼️ Фото' :
                                                step.content_type === 'video' ? '🎬 Видео' : '📷 Альбом'}
                                    </span>
                                    <span className="text-gray-500 text-sm">
                                        ⏱️ {formatDelay(step.delay_seconds)}
                                    </span>
                                    {step.buttons && step.buttons.length > 0 && (
                                        <span className="badge badge-warning">
                                            🔘 {step.buttons.length} кнопок
                                        </span>
                                    )}
                                </div>

                                <p className="text-gray-300 line-clamp-2">
                                    {step.content_text || 'Без текста'}
                                </p>

                                {step.media_files && step.media_files.length > 0 && (
                                    <div className="flex gap-2 mt-3">
                                        {step.media_files.slice(0, 4).map(media => (
                                            <div key={media.id} className="w-16 h-16 rounded-lg overflow-hidden bg-gray-700">
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
                                            </div>
                                        ))}
                                        {step.media_files.length > 4 && (
                                            <div className="w-16 h-16 rounded-lg bg-gray-700 flex items-center justify-center text-gray-400">
                                                +{step.media_files.length - 4}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => openEdit(step)}
                                    className="text-sm px-3 py-1 rounded bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30"
                                >
                                    ✏️
                                </button>
                                <button
                                    onClick={() => handleDelete(step.id)}
                                    className="text-sm px-3 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Create/Edit Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content max-w-xl animate-fade-in max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
                        <h2 className="text-2xl font-bold text-white mb-6">
                            {editingStep ? `Редактировать шаг ${editingStep.step_number}` : `Новый шаг ${formData.step_number}`}
                        </h2>

                        <form onSubmit={handleSubmit}>
                            {/* Delay */}
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Задержка перед отправкой</label>
                                <div className="flex gap-3">
                                    <input
                                        type="number"
                                        min="0"
                                        value={formData.delay_value}
                                        onChange={(e) => setFormData({ ...formData, delay_value: parseInt(e.target.value) || 0 })}
                                        className="input w-24"
                                    />
                                    <select
                                        value={formData.delay_unit}
                                        onChange={(e) => setFormData({ ...formData, delay_unit: e.target.value })}
                                        className="select flex-1"
                                    >
                                        <option value="seconds">Секунды</option>
                                        <option value="minutes">Минуты</option>
                                        <option value="hours">Часы</option>
                                        <option value="days">Дни</option>
                                    </select>
                                </div>
                            </div>

                            {/* Content type */}
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Тип контента</label>
                                <select
                                    value={formData.content_type}
                                    onChange={(e) => setFormData({ ...formData, content_type: e.target.value })}
                                    className="select"
                                >
                                    <option value="text">📝 Текст</option>
                                    <option value="photo">🖼️ Фото</option>
                                    <option value="video">🎬 Видео</option>
                                    <option value="album">📷 Альбом</option>
                                </select>
                            </div>

                            {/* Content text */}
                            <div className="mb-4">
                                <label className="block text-gray-300 mb-2">Текст сообщения</label>
                                <textarea
                                    value={formData.content_text}
                                    onChange={(e) => setFormData({ ...formData, content_text: e.target.value })}
                                    className="textarea h-24"
                                    placeholder="Введите текст сообщения..."
                                />
                            </div>

                            {/* Media selection */}
                            {formData.content_type !== 'text' && (
                                <div className="mb-4">
                                    <label className="block text-gray-300 mb-2">
                                        Медиа ({formData.media_file_ids.length} выбрано)
                                    </label>

                                    <div className="flex gap-2 mb-3">
                                        <input
                                            type="file"
                                            id="file-upload"
                                            multiple
                                            accept="image/*,video/*"
                                            onChange={handleFileUpload}
                                            className="hidden"
                                        />
                                        <label htmlFor="file-upload" className="btn-secondary cursor-pointer text-sm">
                                            📤 Загрузить
                                        </label>
                                    </div>

                                    {mediaFiles.length > 0 ? (
                                        <div className="grid grid-cols-5 gap-2 max-h-32 overflow-y-auto p-2 bg-gray-800/50 rounded-lg">
                                            {mediaFiles.map(media => (
                                                <div
                                                    key={media.id}
                                                    onClick={() => toggleMediaSelection(media.id)}
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
                                            Нет загруженных файлов
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Buttons section - simplified */}
                            <div className="mb-6">
                                <div className="flex items-center justify-between mb-3">
                                    <label className="block text-gray-300 text-sm">Кнопки ({formData.buttons.length})</label>
                                    <button
                                        type="button"
                                        onClick={addButton}
                                        className="text-indigo-400 hover:text-indigo-300 text-sm"
                                    >
                                        + Добавить
                                    </button>
                                </div>

                                {formData.buttons.length > 0 && (
                                    <div className="space-y-3 bg-gray-800/50 rounded-lg p-3">
                                        {formData.buttons.map((btn, index) => (
                                            <div key={index} className="bg-gray-700/50 rounded-lg p-3">
                                                <div className="flex gap-2 mb-2">
                                                    <input
                                                        type="text"
                                                        placeholder="Текст кнопки"
                                                        value={btn.text}
                                                        onChange={(e) => updateButton(index, 'text', e.target.value)}
                                                        className="input text-sm flex-1"
                                                    />
                                                    <button
                                                        type="button"
                                                        onClick={() => removeButton(index)}
                                                        className="text-red-400 hover:text-red-300 px-2"
                                                    >
                                                        ✕
                                                    </button>
                                                </div>
                                                <div className="space-y-2">
                                                    <select
                                                        value={btn.action}
                                                        onChange={(e) => updateButton(index, 'action', e.target.value)}
                                                        className="select text-sm"
                                                    >
                                                        <option value="url">🔗 Ссылка</option>
                                                        <option value="callback">💬 Сообщение</option>
                                                    </select>
                                                    {btn.action === 'url' ? (
                                                        <input
                                                            type="url"
                                                            placeholder="https://example.com"
                                                            value={btn.value}
                                                            onChange={(e) => updateButton(index, 'value', e.target.value)}
                                                            className="input text-sm"
                                                        />
                                                    ) : (
                                                        <textarea
                                                            placeholder="Текст, который отправится при нажатии"
                                                            value={btn.value}
                                                            onChange={(e) => updateButton(index, 'value', e.target.value)}
                                                            className="textarea text-sm"
                                                            rows={3}
                                                        />
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="flex gap-3">
                                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">
                                    Отмена
                                </button>
                                <button type="submit" className="btn-primary flex-1">
                                    {editingStep ? 'Сохранить' : 'Создать'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Media Gallery Modal */}
            {showMediaModal && (
                <div className="modal-overlay" onClick={() => setShowMediaModal(false)}>
                    <div className="modal-content max-w-3xl animate-fade-in" onClick={e => e.stopPropagation()}>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-white">Медиа галерея</h2>
                            <input
                                type="file"
                                id="gallery-upload"
                                multiple
                                accept="image/*,video/*"
                                onChange={handleFileUpload}
                                className="hidden"
                            />
                            <label htmlFor="gallery-upload" className="btn-primary cursor-pointer">
                                📤 Загрузить
                            </label>
                        </div>

                        {mediaFiles.length > 0 ? (
                            <div className="grid grid-cols-4 gap-4 max-h-96 overflow-y-auto">
                                {mediaFiles.map(media => (
                                    <div key={media.id} className="relative group aspect-square rounded-lg overflow-hidden bg-gray-700">
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
                                        <button
                                            onClick={() => handleDeleteMedia(media.id)}
                                            className="absolute top-2 right-2 w-8 h-8 bg-red-500/80 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            🗑️
                                        </button>
                                        <div className="absolute bottom-0 left-0 right-0 bg-black/60 p-2 text-xs truncate">
                                            {media.original_name || media.filename}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-16 text-gray-500">
                                <div className="text-4xl mb-4">📁</div>
                                Нет загруженных файлов
                            </div>
                        )}

                        <button
                            onClick={() => setShowMediaModal(false)}
                            className="btn-secondary w-full mt-6"
                        >
                            Закрыть
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Funnel;
