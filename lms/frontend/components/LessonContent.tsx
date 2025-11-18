"use client";

import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import MultiLanguageCodeBlock from "./MultiLanguageCodeBlock";

interface LessonContentProps {
  content: string;
}

interface MultiLangBlock {
  pythonCode: string;
  cppCode: string;
  javaCode: string;
}

/**
 * Preprocesses markdown to extract :::multilang::: blocks
 * and replace them with placeholders for custom rendering
 */
function preprocessMarkdown(markdown: string): {
  processedMarkdown: string;
  multiLangBlocks: MultiLangBlock[];
} {
  const multiLangBlocks: MultiLangBlock[] = [];

  // Regex to match :::multilang...:::
  const multiLangRegex = /:::multilang\s*([\s\S]*?):::/g;

  const processedMarkdown = markdown.replace(multiLangRegex, (match, content) => {
    // Extract code blocks for each language
    const pythonMatch = content.match(/```python\s*([\s\S]*?)```/);
    const cppMatch = content.match(/```cpp\s*([\s\S]*?)```/);
    const javaMatch = content.match(/```java\s*([\s\S]*?)```/);

    const pythonCode = pythonMatch ? pythonMatch[1].trim() : "";
    const cppCode = cppMatch ? cppMatch[1].trim() : "";
    const javaCode = javaMatch ? javaMatch[1].trim() : "";

    // Store the block
    const index = multiLangBlocks.length;
    multiLangBlocks.push({ pythonCode, cppCode, javaCode });

    // Return placeholder that will be detected and replaced during rendering
    return `<MULTILANG_PLACEHOLDER_${index}>`;
  });

  return { processedMarkdown, multiLangBlocks };
}

export default function LessonContent({ content }: LessonContentProps) {
  // Preprocess content to extract multilang blocks
  const { processedMarkdown, multiLangBlocks } = useMemo(
    () => preprocessMarkdown(content),
    [content]
  );

  return (
    <div className="markdown-content prose prose-slate dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code(props: any) {
            const { node, inline, className, children, ...rest } = props;
            const match = /language-(\w+)/.exec(className || "");
            return !inline && match ? (
              <SyntaxHighlighter
                style={vscDarkPlus as any}
                language={match[1]}
                PreTag="div"
                {...rest}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...rest}>
                {children}
              </code>
            );
          },
          p({ children }) {
            // Check if this paragraph contains a multilang placeholder
            const text = String(children);
            const placeholderMatch = text.match(/^<MULTILANG_PLACEHOLDER_(\d+)>$/);

            if (placeholderMatch) {
              const index = parseInt(placeholderMatch[1], 10);
              const block = multiLangBlocks[index];

              if (block) {
                return (
                  <MultiLanguageCodeBlock
                    pythonCode={block.pythonCode}
                    cppCode={block.cppCode}
                    javaCode={block.javaCode}
                  />
                );
              }
            }

            // Default paragraph rendering
            return <p>{children}</p>;
          },
        }}
      >
        {processedMarkdown}
      </ReactMarkdown>
    </div>
  );
}
