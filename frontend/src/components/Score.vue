<template>
    <button class="button-53" role="button">
        <div class="button-content">
            <div class="title">{{ title }}</div>
            <div class="score">{{ score }}</div>
        </div>
    </button>
</template>

<script setup>

// in <script setup>
defineProps({
    score: Number,
    title: String,
})

</script>
<style scoped>
/* .button-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: .75rem 1.65rem;
} */

.title {
    padding-top: 0%;
    margin-top: -0.5rem;
    height: 15px;
    font-size: 15px;
    color: rgb(29, 29, 29)
}


.score {
    margin-top: 10px;
    font-size: 30px !important
        /* color: #666; */
}

/* CSS */
.button-53 {
    background-color: #ffcb74;
    border: 0 solid #E5E7EB;
    box-sizing: border-box;
    color: #000000;
    display: flex;
    font-family: ui-sans-serif, system-ui, -apple-system, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
    font-size: 1rem;
    font-weight: 700;
    justify-content: center;
    line-height: 1.75rem;
    padding: .75rem 1.65rem;
    position: relative;
    text-align: center;
    text-decoration: none #000000 solid;
    text-decoration-thickness: auto;
    width: 100%;
    max-width: 460px;
    position: relative;
    cursor: pointer;
    /* transform: rotate(-2deg); */
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;
}

.button-53:focus {
    outline: 0;
}

.button-53:after {
    content: '';
    position: absolute;
    border: 1px solid #000000;
    bottom: 4px;
    left: 4px;
    width: calc(100% - 1px);
    height: calc(100% - 1px);
}

.button-53:hover:after {
    bottom: 2px;
    left: 2px;
}
</style>