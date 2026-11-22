function Div(block)
  if block.classes:includes('page-break') and FORMAT:match('docx') then
    return pandoc.RawBlock('openxml',
      '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
  end
end
