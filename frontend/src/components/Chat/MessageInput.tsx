import { useState } from 'react'
import { Input, Button, Space, message as antdMessage } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { useChatStore } from '../../store/chatStore'

const { TextArea } = Input

export default function MessageInput() {
  const { currentConversation, isSending, sendMessage } = useChatStore()
  const [content, setContent] = useState('')

  const handleSend = async () => {
    if (!content.trim() || !currentConversation) {
      return
    }

    try {
      await sendMessage(content.trim())
      setContent('')
    } catch (error) {
      antdMessage.error('发送失败')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div
      style={{
        padding: '16px 24px',
        background: '#fff',
        borderTop: '1px solid #f0f0f0',
      }}
    >
      <Space.Compact style={{ width: '100%' }}>
        <TextArea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入消息... (按 Enter 发送, Shift+Enter 换行)"
          autoSize={{ minRows: 1, maxRows: 6 }}
          disabled={!currentConversation || isSending}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={isSending}
          disabled={!currentConversation || !content.trim()}
        >
          发送
        </Button>
      </Space.Compact>
    </div>
  )
}
