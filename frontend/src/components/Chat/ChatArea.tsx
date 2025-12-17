import { useRef, useEffect } from 'react'
import { Card, Space, Avatar, Typography, Empty, Spin } from 'antd'
import { UserOutlined, RobotOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import { useChatStore } from '../../store/chatStore'
import { formatDate } from '../../utils/format'
import type { Message } from '../../types'

const { Text } = Typography

export default function ChatArea() {
  const { currentConversation, messages, isLoading, isSending } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  if (!currentConversation) {
    return (
      <div
        style={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="选择一个对话或创建新对话开始聊天"
        />
      </div>
    )
  }

  if (isLoading) {
    return (
      <div
        style={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div
      style={{
        height: '100%',
        overflowY: 'auto',
        padding: '24px',
        background: '#f5f5f5',
      }}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
        {isSending && (
          <Card
            style={{
              maxWidth: '80%',
              alignSelf: 'flex-start',
              borderRadius: 12,
            }}
          >
            <Space>
              <Avatar icon={<RobotOutlined />} style={{ background: '#52c41a' }} />
              <Spin />
              <Text type="secondary">正在思考...</Text>
            </Space>
          </Card>
        )}
        <div ref={messagesEndRef} />
      </Space>
    </div>
  )
}

interface MessageItemProps {
  message: Message
}

function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user'

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
      }}
    >
      <Card
        style={{
          maxWidth: '80%',
          background: isUser ? '#1890ff' : '#fff',
          color: isUser ? '#fff' : '#000',
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
        bodyStyle={{ padding: '12px 16px' }}
      >
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Space>
            <Avatar
              icon={isUser ? <UserOutlined /> : <RobotOutlined />}
              style={{ background: isUser ? '#096dd9' : '#52c41a' }}
            />
            <Text strong style={{ color: isUser ? '#fff' : '#000' }}>
              {isUser ? '你' : 'AI'}
            </Text>
            <Text type="secondary" style={{ fontSize: 12, color: isUser ? '#e6f7ff' : '#8c8c8c' }}>
              {formatDate(message.created_at)}
            </Text>
          </Space>
          <div style={{ marginLeft: 40 }}>
            {isUser ? (
              <Text style={{ color: '#fff', whiteSpace: 'pre-wrap' }}>{message.content}</Text>
            ) : (
              <div className="markdown-body">
                <ReactMarkdown
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      return inline ? (
                        <code
                          className={className}
                          style={{
                            background: '#f5f5f5',
                            padding: '2px 6px',
                            borderRadius: 3,
                            fontFamily: 'monospace',
                          }}
                          {...props}
                        >
                          {children}
                        </code>
                      ) : (
                        <pre
                          style={{
                            background: '#282c34',
                            color: '#abb2bf',
                            padding: 16,
                            borderRadius: 8,
                            overflow: 'auto',
                          }}
                        >
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      )
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
            {message.total_tokens && (
              <div style={{ marginTop: 8, fontSize: 12, color: isUser ? '#e6f7ff' : '#8c8c8c' }}>
                <Text type="secondary" style={{ color: isUser ? '#e6f7ff' : '#8c8c8c' }}>
                  Tokens: {message.total_tokens}
                  {message.cost && ` | Cost: $${message.cost.toFixed(6)}`}
                </Text>
              </div>
            )}
          </div>
        </Space>
      </Card>
    </div>
  )
}
