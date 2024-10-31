import { api } from "../boot/axios";

export default {

    async getScores() {
        const params = {
            page: 1,
            per_page: 10,
        };

        try {
            const response = await api.get("/top-score", { params });
            return response.data;

        } catch (error) {
            console.error(error);
        }
    },

    async saveScore(username, score, timeTakenSeconds) {
        try {
            await api.post('/score', {
                username,
                score,
                timeTakenSeconds,
            });
        } catch (error) {
            console.error(error);
        }
    }
}
