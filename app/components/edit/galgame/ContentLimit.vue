<script setup lang="ts">
const props = defineProps<{
  type: 'create' | 'rewrite'
}>()

const { contentLimit } = storeToRefs(usePersistEditGalgameStore())
const { galgamePR } = storeToRefs(useTempGalgamePRStore())

const isNsfw =
  props.type === 'create'
    ? contentLimit.value === 'nsfw'
    : galgamePR.value[0]!.contentLimit === 'nsfw'
const option = ref(isNsfw)

watch(
  () => option.value,
  () => {
    const optionString = option.value ? 'nsfw' : 'sfw'
    if (props.type === 'create') {
      contentLimit.value = optionString
    } else {
      galgamePR.value[0]!.contentLimit = optionString
    }
  }
)
</script>

<template>
  <div class="space-y-2">
    <h2 class="space-x-2 text-xl">
      <span>内容限制</span>
      <span class="font-base text-danger text-sm">新增</span>
    </h2>
    <p class="text-default-500 text-sm">
      
      若没有任何不适宜打开的内容 (例如: 永不枯萎的世界与终结之花), 则默认为 SFW
      (Safe for work)。这将有助于网站索引。
    </p>

    <KunInfo
      color="danger"
      title="再次请大家注意  问题"
      description="网站目前的  认定标准可能比较苛刻, 总之就是越严越好，可以错杀不可以放过，因为会导致网站违反 Google 或 Bing 的条款"
    >
      <p class="text-default-500 text-sm">
         
      </p>
      <div class="flex gap-2">
       <!-- <KunImage alt="nsfw-image2" src="/edit/11.avif" :width="200" />
        <KunImage alt="nsfw-image2" src="/edit/22.avif" :width="200" />-->
      </div>
    </KunInfo>

    <p>请注意这个  开关, 越严越好, 只要有一点不对立即设置为 开启</p>
    <KunSwitch v-model="option" label="开启 " />
  </div>
</template>
