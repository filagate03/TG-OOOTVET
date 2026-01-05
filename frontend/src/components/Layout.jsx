import { Outlet, NavLink, useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { projectsAPI } from '../lib/api';

function Layout() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        loadProject();
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, [id]);

    const loadProject = async () => {
        try {
            const response = await projectsAPI.getById(id);
            setProject(response.data);
        } catch (error) {
            console.error('Failed to load project:', error);
            navigate('/projects');
        }
    };

    const navLinks = [
        { path: 'users', icon: '👥', label: 'Пользователи' },
        { path: 'funnel', icon: '🔄', label: 'Воронка' },
        { path: 'broadcast', icon: '📢', label: 'Рассылки' }
    ];

    return (
        <div className="min-h-screen gradient-bg flex">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="mb-8">
                    <button
                        onClick={() => navigate('/projects')}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
                    >
                        <span>←</span>
                        <span>Проекты</span>
                    </button>

                    {project && (
                        <div className="gradient-card rounded-xl p-4">
                            <h2 className="text-lg font-bold text-white truncate">{project.name}</h2>
                            <p className="text-xs text-gray-400 mt-1 truncate">
                                Token: {project.bot_token.slice(0, 10)}...
                            </p>
                        </div>
                    )}
                </div>

                <nav className="space-y-2">
                    {navLinks.map(link => (
                        <NavLink
                            key={link.path}
                            to={`/project/${id}/${link.path}`}
                            className={({ isActive }) =>
                                `sidebar-link ${isActive ? 'active' : ''}`
                            }
                        >
                            <span className="text-xl">{link.icon}</span>
                            <span>{link.label}</span>
                        </NavLink>
                    ))}
                </nav>

                {/* Current time */}
                <div className="mt-auto pt-8">
                    <div className="text-center text-gray-400 text-sm">
                        <div className="text-2xl font-mono text-white mb-1">
                            {currentTime.toLocaleTimeString('ru-RU')}
                        </div>
                        <div>{currentTime.toLocaleDateString('ru-RU', {
                            weekday: 'long',
                            day: 'numeric',
                            month: 'long'
                        })}</div>
                    </div>
                </div>
            </aside>

            {/* Main content */}
            <main className="flex-1 p-8 overflow-auto">
                <Outlet context={{ project, projectId: parseInt(id) }} />
            </main>
        </div>
    );
}

export default Layout;
