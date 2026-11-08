import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './subjects/SubjectRouter';
import './styles.css';
import './platform/platform.css';

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
