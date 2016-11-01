import { createStore, applyMiddleware, combineReducers } from 'redux';
import thunkMiddleware from 'redux-thunk';
import createLogger from 'redux-logger';
import searchBar from '../reducers/searchBarReducers';
import dashboardTabs from '../reducers/dashboardTabsReducers';
import instruments from '../reducers/instrumentsReducers';
import elements from '../reducers/elementsReducers';
import plots from '../reducers/plotsReducers';
import dataSets from '../reducers/dataSetsReducers';

const loggerMiddleware = createLogger();

const rootReducer = combineReducers({
    searchBar,
    dashboardTabs,
    instruments,
    elements,
    plots,
    dataSets
});

export default function configureStore(preloadedState) {
    return createStore(
        rootReducer,
        preloadedState,
        applyMiddleware(
            thunkMiddleware,
            loggerMiddleware
        )
    );
}
