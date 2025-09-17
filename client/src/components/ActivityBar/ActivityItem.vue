<script setup lang="ts">
import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { faExclamation, faQuestion } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import type { Placement } from "@popperjs/core";
import { computed } from "vue";
import { useRouter } from "vue-router/composables";

import { getGalaxyInstance } from "@/app";
import { useActivityStore } from "@/stores/activityStore";
import type { ActivityVariant } from "@/stores/activityStoreTypes";
import localize from "@/utils/localization";

import GButton from "../BaseComponents/GButton.vue";
import TextShort from "@/components/Common/TextShort.vue";
import Popper from "@/components/Popper/Popper.vue";
import type { Component } from "vue";

const router = useRouter();

interface Option {
    name: string;
    value: string;
}

export interface Props {
    id: string;
    activityBarId: string;
    title?: string;
    icon?: IconDefinition | object;
    indicator?: number;
    isActive?: boolean;
    tooltip?: string;
    tooltipPlacement?: Placement;
    progressPercentage?: number;
    progressStatus?: string;
    options?: Option[];
    to?: string;
    variant?: ActivityVariant;
    windowTitle?: string;
}

const props = withDefaults(defineProps<Props>(), {
    title: undefined,
    icon: () => faQuestion,
    indicator: 0,
    indicatorVariant: "danger",
    isActive: false,
    options: undefined,
    progressPercentage: 0,
    progressStatus: undefined,
    to: undefined,
    tooltip: undefined,
    tooltipPlacement: "right",
    variant: "primary",
    windowTitle: undefined,
});

function isFontAwesome(icon: any): icon is IconDefinition {
  return icon && typeof icon === "object" && "iconName" in icon;
}

const emit = defineEmits<{
    (e: "click"): void;
}>();

function onClick(evt: MouseEvent): void {
    emit("click");
    if (props.to) {
        // Check if it's an external URL
        if (/^https?:\/\//.test(props.to)) {
            window.location.href = props.to;  // full redirect
        } else {
            router.push(props.to);           // internal Vue route
        }
    }
}
const store = useActivityStore(props.activityBarId);
const meta = computed(() => store.metaForId(props.id));
</script>


        <template v-slot:reference   :link-attrs="{ id: `activity-wrapper-${id}` }">
            <b-nav-item
                class="activity-item"
                :class="{ 'nav-item-active': isActive }"
                :link-attrs="{ id: `activity-${id}` }"
                :link-classes="`variant-${props.variant}`"
                :aria-label="localize(title)"
                :disabled="meta?.disabled"
                @click="onClick">
                <span v-if="progressStatus" class="progress">
                    <div
                        class="progress-bar notransition"
                        :class="{
                            'bg-danger': progressStatus === 'danger',
                            'bg-success': progressStatus === 'success',
                        }"
                        :style="{
                            width: `${Math.round(progressPercentage)}%`,
                        }" />
                </span>

                <div class="nav-icon">
                    <!-- Badge indicator -->
                    <span
                    v-if="indicator > 0"
                    class="nav-indicator"
                    data-description="activity indicator"
                    >
                    {{ Math.min(indicator, 99) }}
                    </span>

                    <!-- Render FontAwesome -->
                    <FontAwesomeIcon v-if="isFontAwesome(icon)" :icon="icon" />

                    <!-- Render Lucide (Vue component) -->
                    <component v-else :is="icon" :size="24" stroke-width="2" />
                </div>
                <TextShort v-if="title" :text="localize(title)" class="nav-title" />
            </b-nav-item>
        </template>
        <!-- <div class="text-center px-2 py-1">
            <small v-if="tooltip">{{ localize(tooltip) }}</small>
            <small v-else>No tooltip available for this item</small>
            <div v-if="options" class="nav-options p-1">
                <router-link v-for="(option, index) in options" :key="index" :to="option.value">
                    <GButton size="small" outline color="blue" class="w-100 my-1 text-break text-light">
                        {{ option.name }}
                    </GButton>
                </router-link>
            </div>
        </div> -->


<style scoped lang="scss">
@import "@/style/scss/theme/blue.scss";

.activity-item-popper {
    // Vertically centers the popper in the activity bar
    :deep(.popper-reference-container) {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
}

.activity-item {
      margin-bottom: 8px;
      
      border-radius: 8px;
    position: relative;
    display: flex;
    flex-direction: column;
    width: 5rem;
    padding: 0.5rem;
    margin: 0.125rem 0;

    &:deep(.variant-danger) {
        color: $brand-danger;
    }

    &:deep(.variant-disabled) {
        color: $text-light;
    }
}

.activity-wrapper-workflow {
    color: white;
    background-color: #0a0a0a;
}   

.nav-icon {
    position: relative;
    display: flex;
    justify-content: center;
    cursor: pointer;
    font-size: 1rem;
    color: #0a0a0a88;
    padding: 8px;
   width: fit-content;
   border-radius: 8px;
}

.activity-wrapper-workflow .nav-icon {
    color: white
}

.nav-indicator {
    &.danger-indicator {
        background: $brand-danger;
    }
    &.primary-indicator {
        background: $brand-primary;
    }
    &.disabled-indicator {
        background: $brand-secondary;
    }
    align-items: center;
    border-radius: 50%;
    color: $brand-light;
    display: flex;
    font-size: 0.7rem;
    justify-content: center;
    left: 2.2rem;
    height: 1.2rem;
    position: absolute;
    top: -0.3rem;
    width: 1.2rem;
}

.nav-item-active {
    border-radius: $border-radius-extralarge;
    background: $gray-300;
}

.nav-link {
    padding: 0;
}

.nav-options {
    overflow-x: hidden;
    overflow-y: auto;
}

.nav-title {
    position: relative;
    display: flex;
    justify-content: center;
    margin-top: 0.5rem;
    font-size: 0.7rem;
}

.progress {
    background: transparent;
    border-radius: $border-radius-extralarge;
    position: absolute;
    width: 100%;
    height: 100%;
    left: 0;
    top: 0;
}

.notransition {
    -webkit-transition: none;
    -moz-transition: none;
    -ms-transition: none;
    -o-transition: none;
    transition: none;
}

.nav-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.5rem; // spacing between logo and icon
}

.nav-logo img {
    display: block;
    width: 24px;
    height: 24px;
}

</style>
