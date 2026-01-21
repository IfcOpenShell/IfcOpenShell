import {Home, NotFound} from './pages';

const routes = {
    '/': Home,
    '*': NotFound,
};

export default routes;