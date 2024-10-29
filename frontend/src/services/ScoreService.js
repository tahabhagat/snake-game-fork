import { api } from "../boot/axios";

export default {

    async getScores() {
        console.log("fetching scores");
        const params = {
            page: 1,
            per_page: 10,
        };

        try {
            const response = await api.get("/top-score", { params });
            const data = response.data;
            return data
        } catch (error) {
            console.error(error);
        }
    },

    async sendScoreToSave(username, score, timeTakenSeconds) {
        console.log("saving score");

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
