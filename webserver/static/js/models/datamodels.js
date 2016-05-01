class TableModel {
    constructor(title, data) {
        this.title = title || ''
        this.data = data || []
    }
}

class GraphModel {
    constructor(title) {
        this.title = title || ''
    }
}

export {TableModel, GraphModel}