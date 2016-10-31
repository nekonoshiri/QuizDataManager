from copy import deepcopy
import tkinter as tk
import tkinter.ttk as ttk

from util import findIndex


class ListboxIdd(tk.Listbox):
    def __init__(self, master, **option):
        iddList = option.pop('iddList', [])
        onSelect = option.pop('onSelect', self.onSelectDefault)
        onUnselect = option.pop('onUnselect', self.onUnselectDefault)
        super().__init__(master, **option)
        self.iddList = iddList
        self.onSelect = onSelect
        self.onUnselect = onUnselect


    def _updateList(self):
        self.delete(0, tk.END)
        for _, item in self._iddList:
            self.insert(tk.END, item)


    def _updateOnSelectUnselect(self):
        def listboxSelect(evt):
            if self.selectedIddList:
                self._onSelect(evt)
            else:
                self._onUnselect(evt)
        self.bind('<<ListboxSelect>>', listboxSelect)


    def onSelectDefault(self, evt):
        pass


    def onUnselectDefault(self, evt):
        pass


    @property
    def iddList(self):
        return deepcopy(self._iddList)


    @iddList.setter
    def iddList(self, iddList):
        self._iddList = iddList
        self._updateList()


    @iddList.deleter
    def iddList(self):
        self.iddList = []


    @property
    def onSelect(self):
        return self._onSelect


    @onSelect.setter
    def onSelect(self, onSelect):
        self._onSelect = onSelect
        self._updateOnSelectUnselect()


    @onSelect.deleter
    def onSelect(self):
        self.onSelect = lambda evt: None


    @property
    def onUnselect(self):
        return self._onUnselect


    @onUnselect.setter
    def onUnselect(self, onUnselect):
        self._onUnselect = onUnselect
        self._updateOnSelectUnselect()


    @onUnselect.deleter
    def onUnselect(self):
        self.onUnselect = lambda evt: None


    @property
    def selectedIddList(self):
        selection = self.curselection()
        selectionLen = len(selection)
        if selectionLen == 0:
            return None
        elif selectionLen == 1:
            return [self._iddList[selection[0]]]
        else:
            return [self._iddList[s] for s in selection]


    @property
    def selectedIdList(self):
        sl = self.selectedIddList
        if sl is None:
            return None
        else:
            return [x[0] for x in sl]


    @property
    def selectedIdd(self):
        sil = self.selectedIddList
        if sil is None:
            return None
        else:
            return sil[0]


    @property
    def selectedId(self):
        sil = self.selectedIdList
        if sil is None:
            return None
        else:
            return sil[0]


    def select(self, selectId, throw = False):
        self.select_clear(0, tk.END)
        try:
            ix = findIndex(lambda item: item[0] == selectId,
                self._iddList, True)
            self.select_set(ix)
            self.event_generate('<<ListboxSelect>>')
        except ValueError:
            if throw: raise KeyError("selectId '%s' not found" % selectId)



class ComboboxIdd(ttk.Combobox):
    def __init__(self, master, **option):
        iddList = option.pop('iddList', [])
        onSelect = option.pop('onSelect', self.onSelectDefault)
        super().__init__(master, **option)
        self.iddList = iddList
        self.onSelect = onSelect


    def _updateList(self):
        self['values'] = [item for (_, item) in self._iddList]


    def _updateOnSelect(self):
        self.bind('<<ComboboxSelected>>', self._onSelect)


    def onSelectDefault(self, evt):
        pass


    @property
    def iddList(self):
        return deepcopy(self._iddList)


    @iddList.setter
    def iddList(self, iddList):
        self._iddList = iddList
        self._updateList()


    @iddList.deleter
    def iddList(self):
        self.iddList = []


    @property
    def onSelect(self):
        return self._onSelect


    @onSelect.setter
    def onSelect(self, onSelect):
        self._onSelect = onSelect
        self._updateOnSelect()


    @onSelect.deleter
    def onSelect(self):
        self.onSelect = lambda evt: None


    @property
    def selectedIdd(self):
        selection = self.current()
        if selection == -1:
            return None
        else:
            return self._iddList[selection]


    @property
    def selectedId(self):
        sl = self.selectedIdd
        if sl is None:
            return None
        else:
            return sl[0]

