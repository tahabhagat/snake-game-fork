<template>
    <div class="alert">
        <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span>
        {{ text }}
    </div>
</template>

<script setup>
defineProps({
    text: String,
})</script>

<style>
/* The alert message box */
.alert {
    padding: 20px;
    background-color: #ffcb74;
    /* position: absolute; */
    /* Red */
    color: black;
    /* height: 50px; */
    border-radius: 5px;
    margin-bottom: 10px;
    margin-top: 10px;
    /* margin-bottom: 15px; */
    /* left: 50%;
  transform: translateX(-50%); */
    position: fixed;
    /* bottom: 0; */
    left: 50%;

    transform: translateX(-50%);
}

/* The close button */
.closebtn {
    margin-left: 15px;
    color: rgb(0, 0, 0);
    font-weight: bold;
    float: right;
    font-size: 22px;
    line-height: 20px;
    cursor: pointer;
    transition: 0.3s;
}

/* When moving the mouse over the close button */
.closebtn:hover {
    color: black;
}
</style>