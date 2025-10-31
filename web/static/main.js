// 简单增强：提交前做下必填检查，提示用户
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('convert-form');

  // 初始化日期时间选择器（24小时制，带秒，格式与后端解析兼容）
  if (window.flatpickr) {
    const fpOpts = {
      enableTime: true,
      enableSeconds: true,
      time_24hr: true,
      dateFormat: 'Y-m-d H:i:S',
      allowInput: true,
    };
    window.flatpickr('input[name="contest_start_both"]', fpOpts);
    window.flatpickr('input[name="contest_frozen_time"]', fpOpts);
    window.flatpickr('input[name="contest_end_both"]', fpOpts);
  }

  form.addEventListener('submit', (e) => {
  // 必填校验：比赛名称 + 三个时间，n_name，n_problem，n_sub
    const name = form.querySelector('input[name="contest_name"]')?.value.trim();
    const tStart = form.querySelector('input[name="contest_start_both"]')?.value.trim();
    const tFrozen = form.querySelector('input[name="contest_frozen_time"]')?.value.trim();
    const tEnd = form.querySelector('input[name="contest_end_both"]')?.value.trim();

    const hasProblem = (() => {
      const f = form.querySelector('input[name="n_problem"]');
      const t = form.querySelector('textarea[name="n_problem_text"]');
      const hasFile = f && f.files && f.files.length > 0;
      const hasText = t && t.value.trim().length > 0;
      return hasFile || hasText;
    })();

    const hasName = (() => {
      const f = form.querySelector('input[name="n_name"]');
      const t = form.querySelector('textarea[name="n_name_text"]');
      const hasFile = f && f.files && f.files.length > 0;
      const hasText = t && t.value.trim().length > 0;
      return hasFile || hasText;
    })();

    const hasSub = (() => {
      const f = form.querySelector('input[name="n_sub"]');
      const t = form.querySelector('textarea[name="n_sub_text"]');
      const hasFile = f && f.files && f.files.length > 0;
      const hasText = t && t.value.trim().length > 0;
      return hasFile || hasText;
    })();

    if (!name || !tStart || !tFrozen || !tEnd || !hasName || !hasProblem || !hasSub) {
      e.preventDefault();
      alert('请填写比赛名称与时间（开始/冻结/结束），并提供 n_name.csv、n_problem.csv、n_sub.csv（上传或粘贴其一）。');
    }
  });
});
