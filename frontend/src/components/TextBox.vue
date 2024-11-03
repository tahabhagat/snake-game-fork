<template>

    <div class="changePass">
        <!-- Button to show input -->
        <button v-if="!isFocused" @click="showInput" class="changePassBtn" :style="{ width: buttonWidth }">
            {{ username }}
        </button>

        <!-- Password input field -->
        <input v-show="isFocused" v-model="username" type="text" @blur="hideInput" ref="passwordInput" />
    </div>
</template>
<script setup>
import { ref, nextTick, onMounted } from "vue";

const username = ref("he")


const isFocused = ref(false);
const buttonWidth = ref("auto");
const passwordInput = ref(null);

const showInput = async () => {
    isFocused.value = true;
    await nextTick();
    const newWidth = getComputedStyle(passwordInput.value).width;
    buttonWidth.value = newWidth;
    passwordInput.value.style.width = newWidth;
    passwordInput.value.style.display = "inline-block";
    passwordInput.value.focus();
};

const hideInput = () => {
    isFocused.value = false;
    buttonWidth.value = "auto";
    nextTick(() => {
        passwordInput.value.style.width = "auto";
    });
};

</script>

<style scoped>
.changePass {
    position: relative;
}

.changePass input {
    position: absolute;
    padding: 5px;
    display: none;
}

.changePass .changePassBtn {
    background: #2d89ef;
    border-bottom: 2px solid #2b5797;
    color: white;
    padding: 4px;
    display: inline;
    border-radius: 2px;
    position: absolute;
    overflow: hidden;
    white-space: nowrap;
}

.changePass .changePassBtn:hover {
    background: #2b5797;
    border-top: 2px solid #2d89ef;
    border-bottom: 0;
}
</style>