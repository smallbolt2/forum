<script setup lang="ts"></script>

<template>
  <KunHeader name="发布更新请求">
    <template #endContent>
      <KunCard :is-hoverable="false" content-class="text-sm">
        <p>要更新 Game 信息, 需要提出更新请求</p>
        <p>
          当该请求被该 Game 资源的发布者或论坛管理员确认合并后,
          该更新才会生效
        </p>
        <p>
          若请求更新被合并，请求提出者和审核者会被加入贡献者中，自己修改不计
        </p>
      </KunCard>
      <EditGalgameSite />
    </template>
  </KunHeader>
</template>
