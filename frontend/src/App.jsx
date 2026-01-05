import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Projects from './pages/Projects';
import Users from './pages/Users';
import Funnel from './pages/Funnel';
import Broadcast from './pages/Broadcast';
import Layout from './components/Layout';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/project/:id" element={<Layout />}>
          <Route index element={<Navigate to="users" replace />} />
          <Route path="users" element={<Users />} />
          <Route path="funnel" element={<Funnel />} />
          <Route path="broadcast" element={<Broadcast />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
