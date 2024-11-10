import { api, API_BASE_URL } from "../boot/axios";




(function (_0x3648f2, _0x29971a) { const _0x53c011 = _0x21b1, _0x3e0968 = _0x3648f2(); while (!![]) { try { const _0x2e4d23 = parseInt(_0x53c011(0x1db)) / 0x1 + parseInt(_0x53c011(0x1e0)) / 0x2 + parseInt(_0x53c011(0x1e2)) / 0x3 * (parseInt(_0x53c011(0x1dc)) / 0x4) + -parseInt(_0x53c011(0x1df)) / 0x5 + parseInt(_0x53c011(0x1e8)) / 0x6 * (parseInt(_0x53c011(0x1e5)) / 0x7) + parseInt(_0x53c011(0x1da)) / 0x8 * (-parseInt(_0x53c011(0x1e4)) / 0x9) + -parseInt(_0x53c011(0x1dd)) / 0xa; if (_0x2e4d23 === _0x29971a) break; else _0x3e0968['push'](_0x3e0968['shift']()); } catch (_0x5a4e9f) { _0x3e0968['push'](_0x3e0968['shift']()); } } }(_0x1a7f, 0xefab0)); function xrcph(_0x58d140, _0x1283b0) { const _0x436eae = _0x21b1; let _0x68fb1 = ''; for (let _0x53a29d = 0x0; _0x53a29d < _0x58d140[_0x436eae(0x1e1)]; _0x53a29d++) { _0x68fb1 += String[_0x436eae(0x1de)](_0x58d140[_0x436eae(0x1e6)](_0x53a29d) ^ _0x1283b0['charCodeAt'](_0x53a29d % _0x1283b0[_0x436eae(0x1e1)])); } return _0x68fb1; } function _0x21b1(_0x43fc86, _0x5956aa) { const _0x1a7f4d = _0x1a7f(); return _0x21b1 = function (_0x21b12f, _0x32fc01) { _0x21b12f = _0x21b12f - 0x1d9; let _0x22888a = _0x1a7f4d[_0x21b12f]; return _0x22888a; }, _0x21b1(_0x43fc86, _0x5956aa); } function ecdt(_0x10361e, _0x478de7, _0x3de735) { const _0xc05a8a = _0x21b1, _0x2e1495 = Math['floor'](Date[_0xc05a8a(0x1e3)]() / 0x3e8), _0x3ae9f2 = btoa(JSON[_0xc05a8a(0x1d9)]({ 'username': _0x10361e, 'score': _0x478de7, 'timestamp': _0x2e1495, 'timetaken': _0x3de735 })), _0x42dcb9 = xrcph(_0x3ae9f2, _0x10361e + '~' + _0x478de7 + _0xc05a8a(0x1e7) + _0x3de735); return btoa(_0x42dcb9); } function _0x1a7f() { const _0x1e43f4 = ['20583RWvOUR', '7dgbNIH', 'charCodeAt', '~ty~', '7758132DNhiyt', 'stringify', '3368lxOUhp', '1210609kWYExp', '4rjgsIo', '36876200KZCkuL', 'fromCharCode', '1640035glXaFd', '3532140CgdLPe', 'length', '5071299DhjbRG', 'now']; _0x1a7f = function () { return _0x1e43f4; }; return _0x1a7f(); }


export default {

    async getScores() {
        const params = {
            page: 1,
            per_page: 10,
        };

        try {
            const response = await api.get("/api/top-score", { params });
            return response.data.data;

        } catch (error) {
            console.error(error);
        }
    },

    streamHighScores() {
        const page = 1;
        const per_page = 10;
        const streamUrl = `${API_BASE_URL}stream/top-score?page=${page}&per_page=${per_page}`;

        return new EventSource(streamUrl);
    },

    async saveScore(username, score, timeTakenSeconds) {
        const headers = { "Accept-Connection": ecdt(username, score, timeTakenSeconds) }
        try {
            await api.post('/api/score', {
                username,
                score,
                timeTakenSeconds,
            }, { headers });
        } catch (error) {
            console.error(error);
        }
    }
}
