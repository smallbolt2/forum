<template>
  <div class="flex cursor-pointer items-center gap-3" @click="navigateTo('/')">
    <KunImage
      class="size-10 rounded-2xl"
      src="/favicon.webp"
      :alt="kungal.titleShort"
    />
    <span class="text-2xl font-medium">{{ kungal.name }}</span>
    <KunBadge size="md" color="primary">论坛</KunBadge>
  </div>
</template>
