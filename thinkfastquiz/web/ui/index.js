import { Component, render, h, createRef } from '/ui/preact.mjs'


function call(ws, name, body) {
    ws.send(JSON.stringify({
        name: name,
        body: body
    }))
}

function initRpc(app) {
    var ws = new WebSocket("/api/ws");
    ws.onmessage = (e) => {
        let data = JSON.parse(e.data)
        app.setState({game: data.game, message: data.message})
    };
    ws.onopen = (e) => { call(ws, 'join') }
    return ws;
}

class ThinkFastQuizApp extends Component {
    state = { game: null, message: null };
    answerRef = createRef();

    componentDidMount() {
        this.ws = initRpc(this);
    }

    handleSubmit = (e) => {
        e.preventDefault();
        let { game } = this.state;
        if (game) {
            let answer = this.answerRef.current.value;
            call(this.ws, 'attempt', { position: game.position, answer })
        }
    }

    render() {
        let { game, message } = this.state;
        return (
            h('main', {class: 'container'},
            h('h1', null, 'Think Fast Quiz'),
            h('p', null,
                h('b', null, 'Q: '),
                game ? game.question : "Loading..."),
            h('hr'),
            h('form', {onSubmit: this.handleSubmit},
                h('div', {class: 'form-group'},
                    h('input', {type: 'text', ref: this.answerRef})),
                h('button', {type: 'submit', class: 'btn btn-primary'}, 'Submit')),
            message && h('div', {id: 'message', class: 'alert alert-info', role: 'alert'}, message))
        )
    }
}

render(h(ThinkFastQuizApp), document.body);
