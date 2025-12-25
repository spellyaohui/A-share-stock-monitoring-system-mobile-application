<template>
  <view />
</template>

<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch')
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/common.scss';

page {
  background-color: $bg-primary;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

// 全局涨跌颜色
.text-up {
  color: $up-color !important;
}

.text-down {
  color: $down-color !important;
}

// 隐藏滚动条
::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
</style>
