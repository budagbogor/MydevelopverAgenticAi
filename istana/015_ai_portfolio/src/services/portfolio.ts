import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

const portfolioDirectory = path.join(process.cwd(), 'content/portfolio');

export type PortfolioItem = {
  slug: string;
  title: string;
  category: string;
  description: string;
  size: 'sm' | 'md' | 'lg';
  color: string;
  image: string;
  content: string;
};

export function getAllPortfolios(): PortfolioItem[] {
  // Pastikan direktori ada
  if (!fs.existsSync(portfolioDirectory)) {
    return [];
  }

  const fileNames = fs.readdirSync(portfolioDirectory);
  const allPortfoliosData = fileNames.map((fileName) => {
    // Hilangkan ".md" dari nama file untuk mendapatkan slug
    const slug = fileName.replace(/\.md$/, '');

    // Baca file markdown sebagai string
    const fullPath = path.join(portfolioDirectory, fileName);
    const fileContents = fs.readFileSync(fullPath, 'utf8');

    // Gunakan gray-matter untuk memparsing bagian metadata (frontmatter)
    const matterResult = matter(fileContents);

    // Gabungkan data dengan slug
    return {
      slug,
      content: matterResult.content,
      ...(matterResult.data as Omit<PortfolioItem, 'slug' | 'content'>),
    };
  });

  // Urutkan (misal berdasarkan ukuran atau secara acak)
  return allPortfoliosData as PortfolioItem[];
}
