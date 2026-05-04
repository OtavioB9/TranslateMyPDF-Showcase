const mockJobs = {};

const mockApi = {
  post: async (url, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (url.includes('/upload')) {
          const jobId = 'mock-' + Date.now();
          mockJobs[jobId] = {
            id: jobId,
            status: 'pending',
            progress: 0,
            total_pages: 535,
            current_page: 0,
            eta: 0
          };
          resolve({ data: { job_id: jobId, total_pages: 535 } });
        } else if (url.includes('/translate')) {
          const jobId = url.split('/translate/')[1].split('?')[0];
          mockJobs[jobId].status = 'processing';
          
          if (url.includes('limit_pages=')) {
            const limit = parseInt(url.split('limit_pages=')[1]);
            if (!isNaN(limit)) {
              mockJobs[jobId].total_pages = limit;
            }
          }
          
          let page = 0;
          const total = mockJobs[jobId].total_pages;
          const interval = setInterval(() => {
            page += 4;
            if (page > total) page = total;
            
            mockJobs[jobId].current_page = page;
            mockJobs[jobId].progress = (page / total) * 100;
            mockJobs[jobId].eta = (total - page) * 0.5;
            mockJobs[jobId].current_chapter = `Analisando Seção ${Math.floor(page / 20) + 1}...`;
            
            if (page >= total) {
              mockJobs[jobId].status = 'completed';
              clearInterval(interval);
            }
          }, 1500);
          
          resolve({ data: { message: 'ok' } });
        }
      }, 800);
    });
  },
  get: async (url) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (url.includes('/status')) {
          const jobId = url.split('/status/')[1].split('?')[0];
          resolve({ data: { ...mockJobs[jobId] } });
        }
      }, 200);
    });
  }
};

export default mockApi;
