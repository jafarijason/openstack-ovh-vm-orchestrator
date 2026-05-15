import { useState } from 'react'
import ReactJson from 'react-json-view'
import styles from './MetadataViewer.module.css'

interface MetadataViewerProps {
  metadata?: Record<string, any>
  name?: string
}

export function MetadataViewer({ metadata = {}, name = 'Metadata' }: MetadataViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!metadata || Object.keys(metadata).length === 0) {
    return (
      <div className={`${styles.metadata_viewer} ${styles.empty}`}>
        <p>No metadata available</p>
      </div>
    )
  }

  return (
    <div className={styles.metadata_viewer}>
      <button
        className={styles.metadata_toggle}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className={styles.toggle_icon}>{isExpanded ? '▼' : '▶'}</span>
        <span className={styles.toggle_label}>{name}</span>
        {metadata._raw && (
          <span className={styles.metadata_badge}>_raw payload</span>
        )}
      </button>

      {isExpanded && (
        <div className={styles.metadata_content}>
          <ReactJson
            src={metadata}
            theme="monokai"
            collapsed={2}
            displayDataTypes={true}
            enableClipboard={true}
            onEdit={false}
            onDelete={false}
            onAdd={false}
          />
        </div>
      )}
    </div>
  )
}
