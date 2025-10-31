
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('convert-form');
  const pasteTargets = [
    'n_problem_text',
    'n_name_text',
    'n_sub_text',
    'hoj_sub_text',
  ];

  function csvEscape(s) {
    if (s == null) return '';
    const str = String(s).replace(/\r\n|\r/g, '\n');
    const needsQuote = /[",\n]/.test(str);
    const escaped = str.replace(/"/g, '""');
    return needsQuote ? `"${escaped}"` : escaped;
  }

  function htmlTableToCsv(html) {
    try {
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const table = doc.querySelector('table');
      if (!table) return null;
      const rows = Array.from(table.querySelectorAll('tr'));
      const out = [];
      for (const tr of rows) {
        const cells = Array.from(tr.querySelectorAll('th,td'));
        const rowArr = cells.map(td => csvEscape(td.textContent.trim()));
        // 跳过整行为空
        if (rowArr.join('').length === 0) continue;
        out.push(rowArr.join(','));
      }
      return out.join('\n');
    } catch (e) {
      return null;
    }
  }

  // 从纯文本推断表格并转 CSV
  function plainTextToCsv(text) {
    if (!text) return '';
    const norm = text.replace(/\r\n?|\u2028|\u2029/g, '\n');
    const lines = norm.split('\n');
    const out = [];
    const sample = lines.slice(0, 10).join('\n');
    const hasTab = /\t/.test(sample);
    const hasComma = /,/.test(sample);
    const delim = hasTab ? '\t' : (hasComma ? ',' : /\s{2,}/);
    for (let raw of lines) {
      if (!raw || !raw.trim()) continue;
      let cols;
      if (delim instanceof RegExp) {
        cols = raw.trim().split(delim);
      } else {
        cols = raw.split(delim);
      }
      const row = cols.map(c => csvEscape(c.trim())).join(',');
      out.push(row);
    }
    return out.join('\n');
  }

  function handlePasteToCsv(e) {
    const target = e.target;
    if (!(target && target.tagName === 'TEXTAREA')) return;
    const name = target.getAttribute('name');
    if (!pasteTargets.includes(name)) return;

    const cb = e.clipboardData || window.clipboardData;
    if (!cb) return;
    const html = cb.getData('text/html');
    const text = cb.getData('text/plain');

    // 优先解析 HTML 表格；否则按 TSV 推断
    let csv = null;
    if (html && /<table[\s\S]*?>[\s\S]*<\/table>/i.test(html)) {
      csv = htmlTableToCsv(html);
    }
    if (!csv) {
      csv = plainTextToCsv(text);
    }
    if (csv && csv.trim()) {
      e.preventDefault();
      target.value = csv;
    }
  }

  document.addEventListener('paste', handlePasteToCsv, true);

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
