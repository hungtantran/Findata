export const ADD_ELEMENT = 'ADD_ELEMENT';
export const REMOVE_ELEMENT = 'REMOVE_ELEMENT';

export function addElement(id) {
    return {type: ADD_ELEMENT, id};
}

export function removeElement(elementId) {
    return {type: REMOVE_ELEMENT, elementId};
}
