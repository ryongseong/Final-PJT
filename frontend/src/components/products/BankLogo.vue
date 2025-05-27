<template>
  <div class="bank-logo" :style="{ width: size + 'px', height: size + 'px' }">
    <img v-if="logoUrl" :src="logoUrl" :alt="bankName + ' 로고'" class="bank-logo-img" />
    <div v-else class="bank-logo-fallback">
      {{ bankInitial }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'BankLogo',
  props: {
    bankName: {
      type: String,
      required: true,
    },
    size: {
      type: Number,
      default: 60,
    },
  },
  computed: {
    logoUrl() {
      // Bank logo mapping - add more banks as needed
      const bankLogos = {
        국민은행: 'https://kb-bank.com/assets/img/logo/KB_CI.png',
        신한은행: 'https://image.shinhan.com/rib2017/images/e_ps/cic_shinhan.png',
        우리은행: 'https://www.wooribank.com/img/woori_logo.svg',
        하나은행: 'https://www.kebhana.com/resource/img/logKor.png',
        농협은행: 'https://www.nonghyup.com/content/images/symbol_bi.png',
        기업은행: 'https://www.ibk.co.kr/common/images/common/new/logo/LOGO_IBK.png',
        산업은행: 'https://www.kdb.co.kr/ehp/cms/images/banner/img_kdb_ci.png',
        카카오뱅크: 'https://www.kakaobank.com/static/images/logo/logo.svg',
        토스뱅크: 'https://static.toss.im/toss-logo/toss-logo-blue.png',
        케이뱅크: 'https://www.kbanknow.com/img/pib/kbankbi.png',
        // placeholder URLs, replace with actual logos in production
      }

      // Try exact match
      if (bankLogos[this.bankName]) {
        return bankLogos[this.bankName]
      }

      // Try partial match
      const bankKey = Object.keys(bankLogos).find((bank) => this.bankName.includes(bank))

      return bankKey ? bankLogos[bankKey] : null
    },
    bankInitial() {
      return this.bankName ? this.bankName.charAt(0) : '?'
    },
  },
}
</script>

<style scoped>
.bank-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #f9fafb;
  overflow: hidden;
}

.bank-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.bank-logo-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.5rem;
  color: #3b82f6;
  background-color: #e0f2fe;
}
</style>