import { mount } from 'svelte';
import './css/app.css';
import App from './App.svelte';

const root = document.getElementById('root');
if (!root) {
    throw new Error('Missing root element');
}

const app = mount(App, {
    target: root,
});

export default app;
